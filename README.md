# PPA-projekt
Analiza dostępności punktów usługowych (kościół, przystanki autobusowe, ....) dla powiatów woj. lubelskiego

# PPA_Accessibility_Analysis

## Co robi skrypt
Skrypt pobiera granice administracyjne PRG, wybiera powiaty z gminami wiejskimi i konwertuje dane BDOT10k do geobazy.

## Dane do pobrania
1. BDOT10k (pobrać ręcznie, link: https://opendata.geoportal.gov.pl/bdot10k/schemat2021/SHP/06/06_SHP.ZIP)

## Jak uruchomić
1. Pobierz dane BDOT10k:
   Rozpakować ten zip do pliku 06_SHP w folderze 
   `Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\`
2. Zmienić wszystkie scieżki w kodzie
3. Uruchom skrypt:
   `python Analiza.py`
