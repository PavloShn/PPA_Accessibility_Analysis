import arcpy
import os

from matplotlib import pyplot as plt

arcpy.CheckOutExtension("Network")

# =========================
# ŚCIEŻKI
# =========================
project_gdb = r"C:\Users\pavlo\Documents\ArcGIS\Projects\Projekt_PPA\Projekt_PPA.gdb"
network = os.path.join(project_gdb, "Transport_FD", "Drogi_ND")
powiaty_fc = os.path.join(project_gdb, "Powiaty_w_gminach_wiejskich")
przystanki_fc = os.path.join(project_gdb, "OSM_przystanki_autobusowe")
budynki_fc = os.path.join(project_gdb, "budynki_mieszkalne_all")
koscioly_fc = os.path.join(project_gdb, "OSM_pois_powiaty")

out_gdb = r"C:\Users\pavlo\Documents\SA_WYNIKI.gdb"
if not arcpy.Exists(out_gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(out_gdb), os.path.basename(out_gdb))
print("Utworzono gdb wyjściowe")

# =========================
# LISTY DO WYKRESU
# =========================
powiat_names = []
access_values = []

powiat_names_koscioly = []
access_values_koscioly = []

# ==========================
# POWIATY
# ==========================
powiat_layer = "powiat_lyr"
if not arcpy.Exists(powiat_layer):
    arcpy.management.MakeFeatureLayer(powiaty_fc, powiat_layer)

fields = ["OBJECTID", "JPT_NAZWA_"]

bud_pow_dict = {}  # słownik przechowujący Clip budynków dla każdego powiatu

# =========================
# ANALIZA PRZYSTANKÓW
# =========================
print("=== ANALIZA PRZYSTANKÓW ===")

with arcpy.da.SearchCursor(powiaty_fc, fields) as cursor:
    for oid, name in cursor:
        print(f"\n--- Powiat: {name} ---")

        #Selekcja
        arcpy.management.SelectLayerByAttribute(powiat_layer, "NEW_SELECTION", f"OBJECTID = {oid}")

        bud_pow = os.path.join("in_memory", f"bud_{oid}")
        if not arcpy.Exists(bud_pow):
            arcpy.analysis.Clip(budynki_fc, powiat_layer, bud_pow)
        bud_pow_dict[oid] = bud_pow

        #Clip
        facilities = os.path.join("in_memory", f"fac_bus_{oid}")
        if arcpy.Exists(facilities):
            arcpy.management.Delete(facilities)
        arcpy.analysis.Clip(przystanki_fc, powiat_layer, facilities)

        count_fac = int(arcpy.management.GetCount(facilities)[0])
        print(f"Liczba przystanków: {count_fac}")
        if count_fac == 0:
            print("Brak przystanków w tym powiecie")
            continue

        sa_layer = f"SA_{oid}"

        #Utworzenie Service Area
        arcpy.na.MakeServiceAreaLayer(
            network,
            sa_layer,
            "TIME_MIN",
            "TRAVEL_FROM",
            "15",
            polygon_type="SIMPLE_POLYS",
            merge="NO_MERGE"
        )
        print("✔ Service Area Layer utworzona")

        #Dodanie Facilities
        sub_layers = arcpy.na.GetNAClassNames(sa_layer)
        fac_sub = sub_layers["Facilities"]
        arcpy.na.AddLocations(sa_layer, fac_sub, facilities, search_tolerance="500 Meters")
        print("✔ Facilities dodane")

        #Solve
        arcpy.na.Solve(sa_layer)
        print("✔ SOLVE wykonany")

        #Eksport
        poly_sub = sub_layers["SAPolygons"]
        out_fc = os.path.join(out_gdb, f"SA_bus_{oid}")

        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)


        arcpy.management.CopyFeatures(f"{sa_layer}\\{poly_sub}", out_fc)
        print(f"✔ Poligony dla powiatu zapisane: {out_fc}")

        sa_diss = os.path.join("in_memory", f"sa_diss_{oid}")

        if arcpy.Exists(sa_diss):
            arcpy.management.Delete(sa_diss)

        arcpy.management.Dissolve(
            in_features=out_fc,   
            out_feature_class=sa_diss
        )

        # =========================
        # BUDYNKI – LICZENIE
        # =========================
        bud_pow_used = bud_pow_dict[oid]

        total_bud = int(arcpy.management.GetCount(bud_pow)[0])

        bud_in = os.path.join("in_memory", f"bud_in_{oid}")

        if arcpy.Exists(bud_in):
            arcpy.management.Delete(bud_in)

        arcpy.analysis.Intersect(
            [bud_pow_used, sa_diss],
            bud_in
        )

        in_range = int(arcpy.management.GetCount(bud_in)[0])
        percent = round((in_range / total_bud) * 100, 2) if total_bud > 0 else 0

        print(f"Budynki w zasięgu: {in_range}")
        print(f"Wszystkie budynki: {total_bud}")
        print(f"Dostępność: {percent}%")

        powiat_names.append(name)
        access_values.append(percent)

# ==========================
# WYKRES PNG PRZYSTANKI
# ==========================

plt.figure(figsize=(12, 6))
plt.bar(powiat_names, access_values)
plt.ylabel("Dostępność [%]")
plt.xlabel("Powiat")
plt.title("Dostępność piesza do przystanków autobusowych (15 min)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

out_png = r"D:\Projekt_Zaliczyniowy_PPA\dostepnosc_przystanki_powiaty.png" ##Podaj scięzke do wykresu
plt.savefig(out_png, dpi=300)
plt.close()

print(f"\n Wykres analizy przystanków zapisany: {out_png}")

#==================================
# ANALIZA DOSTĘPNOŚCI KOŚCIOŁÓW
#==================================
print("=== ANALIZA KOŚCIOŁÓW ===")

with arcpy.da.SearchCursor(powiaty_fc, fields) as cursor2:
    for oid, name in cursor2:
        print(f"\n--- Powiat: {name} ---")

        #Selekcja
        arcpy.management.SelectLayerByAttribute(powiat_layer, "NEW_SELECTION", f"OBJECTID = {oid}")

        #Clip
        facilities_kosciol = os.path.join("in_memory", f"fac_kosciol_{oid}")
        if arcpy.Exists(facilities_kosciol):
            arcpy.management.Delete(facilities_kosciol)
        arcpy.analysis.Clip(koscioly_fc, powiat_layer, facilities_kosciol)

        count_fac = int(arcpy.management.GetCount(facilities_kosciol)[0])
        print(f"Liczba kościolów: {count_fac}")
        if count_fac == 0:
            print("Brak kościolów w tym powiecie")
            continue

        sa_layer_kosciol = f"SA__kosciol_{oid}"

        #Utworzenie Service Area
        arcpy.na.MakeServiceAreaLayer(
            network,
            sa_layer_kosciol,
            "TIME_MIN",
            "TRAVEL_FROM",
            "15",
            polygon_type="SIMPLE_POLYS",
            merge="NO_MERGE"
        )
        print("✔ Service Area Layer utworzona")

        #Dodanie Facilities
        sub_layers_kosciol = arcpy.na.GetNAClassNames(sa_layer_kosciol)
        fac_sub_kosciol = sub_layers_kosciol["Facilities"]
        arcpy.na.AddLocations(sa_layer_kosciol, fac_sub_kosciol , facilities_kosciol, search_tolerance="500 Meters")
        print("✔ Facilities dodane")

        #Solve
        arcpy.na.Solve(sa_layer_kosciol)
        print("✔ SOLVE wykonany")

        #Eksport
        poly_sub_kosciol = sub_layers_kosciol["SAPolygons"]
        out_fc_kosciol = os.path.join(out_gdb, f"SA_kosciol_{oid}")

        if arcpy.Exists(out_fc_kosciol):
            arcpy.management.Delete(out_fc_kosciol)


        arcpy.management.CopyFeatures(f"{sa_layer_kosciol}\\{poly_sub_kosciol}", out_fc_kosciol)
        print(f"✔ Poligony dla powiatu zapisane: {out_fc_kosciol}")

        sa_diss_kosciol = os.path.join("in_memory", f"sa_diss_kosciol_{oid}")

        if arcpy.Exists(sa_diss_kosciol):
            arcpy.management.Delete(sa_diss_kosciol)

        arcpy.management.Dissolve(
            in_features=out_fc_kosciol,   
            out_feature_class=sa_diss_kosciol
        )

        # ========================
        # BUDYNKI – LICZENIE
        # ========================
        bud_pow_used = bud_pow_dict[oid]  # już mamy Clip zrobiony wcześniej

        total_bud_kosciol = int(arcpy.management.GetCount(bud_pow_used)[0])

        bud_in_kosciol = os.path.join("in_memory", f"bud_in_kosciol_{oid}")

        if arcpy.Exists(bud_in_kosciol):
            arcpy.management.Delete(bud_in_kosciol)

        arcpy.analysis.Intersect(
            [bud_pow_used, sa_diss_kosciol],
            bud_in_kosciol
        )

        in_range_kosciol = int(arcpy.management.GetCount(bud_in_kosciol)[0])
        percent_kosciol = round((in_range_kosciol / total_bud_kosciol) * 100, 2) if total_bud_kosciol > 0 else 0

        print(f"Budynki w zasięgu: {in_range_kosciol}")
        print(f"Wszystkie budynki: {total_bud_kosciol}")
        print(f"Dostępność: {percent_kosciol}%")

        powiat_names_koscioly.append(name)
        access_values_koscioly.append(percent_kosciol)



# ==========================
# WYKRES PNG KOŚCIOŁY
# ==========================

plt.figure(figsize=(12, 6))
plt.bar(powiat_names_koscioly, access_values_koscioly)
plt.ylabel("Dostępność [%]")
plt.xlabel("Powiat")
plt.title("Dostępność piesza do kościołów (15 min)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

out_png = r"D:\Projekt_Zaliczyniowy_PPA\dostepnosc_koscioly_powiaty.png" ##Podaj scięzke do wykresu
plt.savefig(out_png, dpi=300)
plt.close()

print(f"\n Wykres zapisany: {out_png}")

print("KONIEC")