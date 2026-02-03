# PPA-projekt
Analiza dostępności punktów usługowych (kościół, przystanki autobusowe, ....) dla powiatów woj. lubelskiego

# PPA_Accessibility_Analysis

## Co robi skrypt
Skrypt pobiera granice administracyjne PRG, wybiera powiaty z gminami wiejskimi i konwertuje dane BDOT10k do geobazy.

## Dane do pobrania
1. BDOT10k (pobrać ręcznie, link: https://umcso365-my.sharepoint.com/:u:/g/personal/320172_office_umcs_pl/IQAZmC5ah5M3RZYOkS0wMkQcAfIzgg8-pLM08M2tRQEbgrU?e=qksgeL)

## Przygotowanie Network Dataset w ArcGIS Pro:
1. **Utworzenie Network Dataset**
   - Target Feature Dataset: `Transport_FD`
   - Network Dataset Name: `Drogi_ND`
   - Source Feature Class: `Drogi_all_FD`
   - Elevation Model: `No elevations`

2. **Build Network**
   - PPM → Build Network

3. **Travel Attributes**
   - Dodaj Cost:
     - Name: `TIME_MIN`
     - Units: `Minutes`
     - Data Type: `Double`
   - Evaluators:
     - Edges:
       - `Drogi_all_FD (Along)`: Type = Field Script → Value = `!TIME_MIN!`
       - `Drogi_all_FD (Against)`: Type = Same as Along → Value = `!TIME_MIN!`

4. **Travel Mode**
   - New:
     - Name: `TIME_MIN`
     - Type: `Walking`
     - Impedance: `TIME_MIN`

5. **Build Network** ponownie

## Jak uruchomić
1. Pobierz dane BDOT10k:
   Rozpakować ten zip do pliku 06_SHP w folderze 
   `Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\`
2. Zmienić wszystkie scieżki w obu plikach
3. Uruchom skrypt:
   `analiza_1.py`
4. Uruchom skrypt:
   `analiza_2.py`
