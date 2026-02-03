import arcpy
import os

arcpy.CheckOutExtension("Network")

# -------------------------
# ŚCIEŻKI
# -------------------------
project_gdb = r"C:\Users\pavlo\Documents\ArcGIS\Projects\Projekt_PPA\Projekt_PPA.gdb"
network = os.path.join(project_gdb, "Transport_FD", "Drogi_ND")
powiaty_fc = os.path.join(project_gdb, "Powiaty_w_gminach_wiejskich")
przystanki_fc = os.path.join(project_gdb, "OSM_przystanki_autobusowe")

out_gdb = r"C:\Users\pavlo\Documents\SA_WYNIKI.gdb"
if not arcpy.Exists(out_gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(out_gdb), os.path.basename(out_gdb))
print("Utworzono gdb wyjściowe")

# -------------------------
# POWIATY
# -------------------------
powiat_layer = "powiat_lyr"
if not arcpy.Exists(powiat_layer):
    arcpy.management.MakeFeatureLayer(powiaty_fc, powiat_layer)

fields = ["OBJECTID", "JPT_NAZWA_"]

# -------------------------
# ITERACJA
# -------------------------
with arcpy.da.SearchCursor(powiaty_fc, fields) as cursor:
    for oid, name in cursor:
        print(f"\n--- Powiat: {name} ---")

        #Selekcja
        arcpy.management.SelectLayerByAttribute(powiat_layer, "NEW_SELECTION", f"OBJECTID = {oid}")

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
            polygon_type="DETAILED_POLYS",
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

print("KONIEC")