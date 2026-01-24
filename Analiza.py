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
powiaty = powiaty = os.path.join(extract_dir, "A02_Granice_powiatow.shp")

#====================================================================================================================
# WYZNACZANIE POWIATÓW Z GMINAMI WIEJSKIMI
#====================================================================================================================
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

# ===================================================================================================================
# KONWERSACJA DANYCH BDOT10K
# ===================================================================================================================

#scieżka folderów

##Wypakój dane BDOT10k do folderu 06_SHP
folder_shp = r"D:\Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\06_SHP" 

#Listowanie plików w os
for file in os.listdir(folder_shp):
    name, ext = os.path.splitext(file)
    #print(name, ext)

    new_name = name.replace(".","_") + ext
    #print(new_name)
    shutil.copy(f"{folder_shp}\\{file}", f"{folder_shp_new}\\{new_name}")

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
                arcpy.management.Delete(out_fc)

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
            




print("KONIEC")