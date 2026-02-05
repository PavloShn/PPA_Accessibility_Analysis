import zipfile
import arcpy
import os
import shutil

import urllib

# ==========================================================
# ŚCIEŻKI
# ==========================================================

gdb = r"C:\Users\pavlo\Documents\ArcGIS\Projects\Projekt_PPA\Projekt_PPA.gdb"
arcpy.env.workspace = gdb

katalog = r"D:\Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy"
zip_path = os.path.join(katalog, "PRG_jednostki.zip")
extract_dir = os.path.join(katalog, "PRG")

folder_shp_new = r"D:\Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\new_06_SHP"
os.makedirs(folder_shp_new, exist_ok=True)
# ===================================================================================================================
# POBIERANIE DANYCH
# ===================================================================================================================
link_granice = "https://opendata.geoportal.gov.pl/prg/granice/00_jednostki_administracyjne.zip"

os.makedirs(extract_dir, exist_ok=True)


if not os.path.exists(zip_path):
    urllib.request.urlretrieve(link_granice, zip_path)
    print("ZIP PRG pobrany")
else:
    print("ZIP PRG już istnieje")

if not any(os.scandir(extract_dir)):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    print("ZIP PRG rozpakowany")
else:
    print("Dane PRG już rozpakowane – pomijam")


gminy = os.path.join(extract_dir, "A05_Granice_jednostek_ewidencyjnych.shp")
powiaty = os.path.join(extract_dir, "A02_Granice_powiatow.shp")

# ====================================================================================================================
# WYZNACZANIE POWIATÓW Z GMINAMI WIEJSKIMI
# ====================================================================================================================
arcpy.management.MakeFeatureLayer(gminy, "gminy_lyr")
arcpy.management.MakeFeatureLayer(powiaty, "powiaty_lyr")

arcpy.management.SelectLayerByAttribute(
    "gminy_lyr",
    "NEW_SELECTION",
    "JPT_NAZWA_ LIKE '%gmina wiejska' AND JPT_KOD_JE LIKE '06%'"
)

arcpy.management.SelectLayerByLocation(
    "powiaty_lyr",
    "CONTAINS",
    "gminy_lyr",
    selection_type="NEW_SELECTION"
    )

out_powiaty = r"C:\Users\pavlo\Documents\ArcGIS\Projects\Projekt_PPA\Projekt_PPA.gdb\Powiaty_w_gminach_wiejskich"
if not arcpy.Exists(out_powiaty):
    arcpy.management.CopyFeatures("powiaty_lyr", out_powiaty)
    print("Zapisane do geobazy")
else:
    print("Powiaty_w_gminach_wiejskich już istnieje — pomijam zapis")

print("Zapisane do geobazy")

powiaty_fc = os.path.join(gdb, "Powiaty_w_gminach_wiejskich")

# ===================================================================================================================
# KONWERSACJA DANYCH BDOT10K
# ===================================================================================================================

# #scieżka folderów

# Wypakuj dane BDOT10k do folderu 06_SHP
folder_shp = r"D:\Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\06_SHP" 

#Listowanie plików w os
if not any(os.scandir(folder_shp_new)):
    print("Kopiuję pliki BDOT10k do folderu roboczego...")
    for file in os.listdir(folder_shp):
        name, ext = os.path.splitext(file)
        new_name = name.replace(".", "_") + ext
        shutil.copy(
            os.path.join(folder_shp, file),
            os.path.join(folder_shp_new, new_name)
        )
else:
    print("Folder new_06_SHP już zawiera dane — pomijam kopiowanie")

for file in os.listdir(folder_shp_new):
    name, ext = os.path.splitext(file)

    if ext.lower() == ".shp":
        print("Plik:", file)

        if "__" not in name:
            continue

        new_name = name.split("__")[1]
        print("Typ:", new_name)

        if "BUBD" in new_name.upper():
            shp_path = os.path.join(folder_shp_new, file)

            layer_name = f"lyr_budynki_{new_name}"
            out_fc = os.path.join(gdb, f"budynki_mieszkalne_{new_name}")

            if arcpy.Exists(out_fc):
                print(f"{out_fc} już istnieje — pomijam")
                continue

            arcpy.management.MakeFeatureLayer(shp_path, layer_name)
            arcpy.management.SelectLayerByAttribute(
                layer_name,
                "NEW_SELECTION",
                "FOBUD = 'budynki mieszkalne'"
            )

            # sprawdzenie czy coś wybrano
            count = int(arcpy.management.GetCount(layer_name)[0])
            print("Zaznaczone obiekty:", count)

            if count > 0:
                arcpy.conversion.ExportFeatures(layer_name, out_fc)
                print("✔ Zapisano:", out_fc)
            else:
                print("ℹ Brak budynków mieszkalnych")
        elif ("SKDR" in new_name.upper()):
            shp_path = os.path.join(folder_shp_new, file)

            layer_name = f"lyr_drogi_{new_name}"
            out_fc = os.path.join(gdb, f"Drogi_{new_name}")

            if arcpy.Exists(out_fc):
                arcpy.management.Delete(out_fc)

            arcpy.management.MakeFeatureLayer(shp_path, layer_name)
            
            count = int(arcpy.management.GetCount(layer_name)[0])
            print("Drogi zaznaczone:", count)

            if count > 0:
                arcpy.conversion.ExportFeatures(layer_name, out_fc)
                print("Zapisano drogi do GDB:", out_fc)
            else:
                print("Brak dróg do analizy")
        elif ("SKRP" in new_name.upper()):
            shp_path = os.path.join(folder_shp_new, file)

            layer_name = f"lyr_drogi_{new_name}"
            out_fc = os.path.join(gdb, f"Drogi_{new_name}")

            if arcpy.Exists(out_fc):
                arcpy.management.Delete(out_fc)

            arcpy.management.MakeFeatureLayer(shp_path, layer_name)
            
            count = int(arcpy.management.GetCount(layer_name)[0])
            print("Drogi zaznaczone:", count)

            if count > 0:
                arcpy.conversion.ExportFeatures(layer_name, out_fc)
                print("Zapisano drogi do GDB:", out_fc)
            else:
                print("Brak dróg do analizy")

# ============================================================================================
# OSM pobieranie
# ============================================================================================
link_OSM = "https://download.geofabrik.de/europe/poland/lubelskie-260131-free.shp.zip"

zip_path_OSM = os.path.join(katalog, "OSM_pkt.zip")
extract_dir_OSM = os.path.join(katalog, "OSM")

os.makedirs(extract_dir_OSM, exist_ok=True)


if not os.path.exists(zip_path_OSM):
    urllib.request.urlretrieve(link_OSM, zip_path_OSM)
    print("ZIP OSM pobrany")
else:
    print("ZIP OSM już istnieje")

if not any(os.scandir(extract_dir_OSM)):
    with zipfile.ZipFile(zip_path_OSM, "r") as zip_ref_OSM:
        zip_ref_OSM.extractall(extract_dir_OSM)

    print("ZIP OSM rozpakowany")
else:
    print("Dane OSM już rozpakowane – pomijam")

osm_transport = os.path.join(extract_dir_OSM, "gis_osm_transport_free_1.shp")
osm_pois = os.path.join(extract_dir_OSM, "gis_osm_pois_free_1.shp")
# ============================================================================================
# OSM przystanki autobusowe
# ============================================================================================
            
osm_transport_clip = os.path.join(gdb, "OSM_transport_powiaty")

if not arcpy.Exists(osm_transport_clip):
    arcpy.analysis.Clip(
        in_features=osm_transport,
        clip_features=powiaty_fc,
        out_feature_class=osm_transport_clip
    )
    print("✔ OSM transport przycięty do powiatów")
else:
    print("OSM_transport_powiaty już istnieje")

out_stops = os.path.join(gdb, "OSM_przystanki_autobusowe")

if not arcpy.Exists(out_stops):
    arcpy.management.MakeFeatureLayer(
        osm_transport_clip,
        "osm_transport_lyr"
    )

    arcpy.management.SelectLayerByAttribute(
        "osm_transport_lyr",
        "NEW_SELECTION",
        "fclass = 'bus_stop'"
    )

    count = int(arcpy.management.GetCount("osm_transport_lyr")[0])
    print("Przystanki autobusowe:", count)

    if count > 0:
        arcpy.conversion.ExportFeatures(
            "osm_transport_lyr",
            out_stops
        )
        print("✔ Zapisano przystanki autobusowe")
else:
    print("OSM_przystanki_autobusowe już istnieją")


# ===========================================================================================
# OSM kościoły
# ===========================================================================================

osm_pois_clip = os.path.join(gdb, "OSM_pois_powiaty")

if not arcpy.Exists(osm_pois_clip):
    arcpy.analysis.Clip(
        in_features=osm_pois,
        clip_features=powiaty_fc,
        out_feature_class=osm_pois_clip
    )
    print("✔ OSM POI przycięte do powiatów")
else:
    print("OSM_pois_powiaty już istnieje")

out_churches = os.path.join(gdb, "OSM_koscioly")

if not arcpy.Exists(out_churches):
    arcpy.management.MakeFeatureLayer(
        osm_pois_clip,
        "osm_pois_lyr"
    )
    church_types = ("graveyard", "wayside_shrine", "wayside_cross")
    church_types_sql = "','".join(church_types)
    arcpy.management.SelectLayerByAttribute(
        "osm_pois_lyr",
        "NEW_SELECTION",
        f"fclass IN ('{church_types_sql}')"
    )

    count = int(arcpy.management.GetCount("osm_pois_lyr")[0])
    print("Kościoły:", count)

    if count > 0:
        arcpy.conversion.ExportFeatures(
            "osm_pois_lyr",
            out_churches
        )
        print("✔ Zapisano kościoły")
else:
    print("OSM_koscioly już istnieją")

# ============================================================================================
# MERGE BUDYNKÓW
# ============================================================================================

budynki_list = arcpy.ListFeatureClasses("budynki_mieszkalne_OT_BUBD_A*")
budynki_all = os.path.join(gdb, "budynki_mieszkalne_all")

if not arcpy.Exists(budynki_all):
    arcpy.management.Merge(budynki_list, budynki_all)
    print("✔ Scalono warstwy budynków:", budynki_list)
else:
    print("budynki_mieszkalne_all już istnieje")

# ============================================================================================
# MERGE DRÓG
# ============================================================================================

drogi_all = os.path.join(gdb, "Drogi_all")


if not arcpy.Exists(drogi_all):
    arcpy.management.Merge(
        arcpy.ListFeatureClasses("Drogi_*"),
        drogi_all
    )
    print("✔ Scalono drogi")

if "TIME_MIN" not in [f.name for f in arcpy.ListFields(drogi_all)]:
    arcpy.management.AddField(drogi_all, "TIME_MIN", "DOUBLE")

# długość w metrach / 83.33 = minuty
arcpy.management.CalculateField(
    drogi_all,
    "TIME_MIN",
    "!shape.length@meters! / 83.33",
    "PYTHON3"
)

print("✔ Dodano czas przejścia po drogach")

# ============================================================================================
# TWORZENIE FEATURE DATASET
# ============================================================================================

fd_name = "Transport_FD"
sp_ref = arcpy.Describe(drogi_all).spatialReference

if not arcpy.Exists(os.path.join(gdb, fd_name)):
    arcpy.management.CreateFeatureDataset(
        gdb, fd_name, sp_ref
    )
    print("✔ Feature Dataset utworzone")
else:
    print("Feature Dataset już istnieje")

drogi_fd = os.path.join(gdb, fd_name, "Drogi_all_FD")
if not arcpy.Exists(drogi_fd):
    arcpy.management.CopyFeatures(drogi_all, drogi_fd)
    print("✔ Drogi skopiowane do Feature Dataset")
else:
    print("Drogi już są w Feature Dataset")

print("KONIEC")
