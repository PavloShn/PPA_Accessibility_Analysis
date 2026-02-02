#NIEDOKOŃCZONE

import arcpy
from arcpy import nax
import os

print("===== START ANALIZY SERVICE AREA =====\n")

arcpy.CheckOutExtension("Network")

# --------------------------------------------------
# ŚCIEŻKI
# --------------------------------------------------
project_gdb = r"C:\Users\pavlo\Documents\ArcGIS\Projects\Projekt_PPA\Projekt_PPA.gdb"
network = os.path.join(project_gdb, "Transport_FD", "Drogi_ND")

powiaty_fc = os.path.join(project_gdb, "Powiaty_w_gminach_wiejskich")
przystanki_fc = os.path.join(project_gdb, "OSM_przystanki_autobusowe")

# --------------------------------------------------
# OUTPUT GDB (TYLKO GDB – INACZEJ NIE ZADZIAŁA)
# --------------------------------------------------
out_gdb = r"C:\Users\pavlo\Documents\SA_WYNIKI.gdb"
if not arcpy.Exists(out_gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(out_gdb), os.path.basename(out_gdb))

# --------------------------------------------------
# WARSTWA POWIATÓW
# --------------------------------------------------
powiat_layer = "powiat_lyr"
if not arcpy.Exists(powiat_layer):
    arcpy.management.MakeFeatureLayer(powiaty_fc, powiat_layer)

fields = ["OBJECTID", "JPT_NAZWA_"]

# --------------------------------------------------
# ITERACJA PO POWIATACH
# --------------------------------------------------
with arcpy.da.SearchCursor(powiaty_fc, fields) as cursor:
    for oid, name in cursor:

        print(f"\n--- Powiat: {name} ---")

        arcpy.management.SelectLayerByAttribute(powiat_layer, "NEW_SELECTION", f"OBJECTID = {oid}")

        # -------------------------------
        # CLIP
        # -------------------------------
        facilities = os.path.join("in_memory", f"fac_bus_{oid}")
        if arcpy.Exists(facilities):
            arcpy.management.Delete(facilities)

        arcpy.analysis.Clip(przystanki_fc, powiat_layer, facilities)

        count_fac = int(arcpy.management.GetCount(facilities)[0])
        print(f"Liczba przystanków: {count_fac}")

        if count_fac == 0:
            print("Brak przystanków – pomijam")
            continue

        # -------------------------------
        # SERVICE AREA
        # -------------------------------
        sa = nax.ServiceArea(network)
        sa.travelMode = "TIME_MIN"
        sa.load(nax.ServiceAreaInputDataType.Facilities, facilities)

        result = sa.solve()

        if not result.solveSucceeded:
            print("❌ Solver NIE powiódł się")
            continue

        print("✔ Solver OK")

        # -------------------------------
        # EXPORT POLYGONÓW (GDB)
        # -------------------------------
        result.export(nax.ServiceAreaOutputDataType.Polygons, out_gdb)
        print(f"✔ Poligony zapisane do GDB: {out_gdb}")

print("\n===== KONIEC ANALIZY =====")