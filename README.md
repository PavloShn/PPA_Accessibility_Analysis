# Accessibility Analysis Lublin

Analiza dostępności punktów usługowych (kościoły, przystanki autobusowe) dla powiatów województwa lubelskiego z gminami wiejskimi.

## Opis projektu

Projekt składa się z dwóch głównych skryptów:

- `DataInst.py` – przygotowuje dane wejściowe (granice administracyjne PRG, powiaty z gminami wiejskimi) i konwertuje dane BDOT10k do geobazy.
- `Analiza_Dost.py` – przeprowadza analizę dostępności punktów usługowych w poszczególnych powiatach, generuje poligony Service Area oraz wykresy dostępności pieszej.

---

## Co robi skrypt

- Pobiera granice administracyjne PRG.
- Wybiera powiaty z gminami wiejskimi.
- Konwertuje dane BDOT10k do geobazy w ArcGIS Pro.
- Analizuje dostępność punktów usługowych (kościoły, przystanki autobusowe) w czasie dojścia pieszo do 15 minut.
- Tworzy Service Area (poligony dostępności) dla każdego powiatu.
- Liczy budynki mieszkalne w zasięgu każdego Service Area.
- Generuje wykresy dostępności dla powiatów.

---

## Dane do pobrania

- BDOT10k – ręcznie pobrać z linku: [BDOT10k](https://umcso365-my.sharepoint.com/:u:/g/personal/320172_office_umcs_pl/IQAZmC5ah5M3RZYOkS0wMkQcAfIzgg8-pLM08M2tRQEbgrU?e=qksgeL)
- Rozpakuj pliki zip do folderu `Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\`.

---
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

1. Pobierz dane BDOT10k i rozpakuj ZIP do folderu:
   `Projekt_Zaliczyniowy_PPA\Dane_PPA_Projekt_Zaliczyniowy\`.
2. Zmień wszystkie ścieżki w obu plikach skryptów (`DataInst.py` i `Analiza_Dost.py`) tak, aby wskazywały na odpowiednie lokalizacje danych i geobazę wyjściową.
3. Uruchom skrypty w kolejności:
   1. `DataInst.py`
   2. **Po uruchomieniu `DataInst.py` należy ręcznie w ArcGIS Pro utworzyć Network Dataset w docelowym Feature Dataset (`Transport_FD`).**
   3. `Analiza_Dost.py`
