# PPA-projekt
Analiza dostępności punktów usługowych (kościół, przystanki autobusowe, ....) dla powiatów woj. lubelskiego

# PPA_Accessibility_Analysis

## Co robi skrypt
Skrypt pobiera granice administracyjne PRG, wybiera powiaty z gminami wiejskimi i konwertuje dane BDOT10k do geobazy.

## Dane do pobrania
1. BDOT10k (pobrać ręcznie, link: https://umcso365-my.sharepoint.com/:u:/g/personal/320172_office_umcs_pl/IQAZmC5ah5M3RZYOkS0wMkQcAfIzgg8-pLM08M2tRQEbgrU?e=qksgeL)

## Jak uruchomić
1. Pobierz dane BDOT10k:
   Rozpakować ten zip do pliku 06_SHP w folderze 
   `Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\`
2. Zmienić wszystkie scieżki w kodzie
3. Uruchom skrypt:
   `python Analiza.py`
