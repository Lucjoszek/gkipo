# Analiza jakości zdjęć na podstawie automatycznej oceny histogramu

![Podgląd](assets/readme/wynik_programu.png)

1. Pobranie obrazu z Internetu (`urllib.request`).
2. Analiza jakości obrazu.
3. Odczytanie głębi bitowej obrazu (zastosowanie `Image.histogram()` ograniczałoby do obrazów 8-bitowych). 
4. Wydobycie histogramu całego obrazu oraz poszczególnych kanałów RGB (rozdzielenie kanałów `Image.split()`).
5. Utworzenie układu (`matplotlib.pyplot.subplot_mosaic`):
  * po lewej - oryginalny obraz,
  * po prawej - cztery histogramy 2x2:
    * histogram wszystkich kanałów,
    * histogram kanału R,
    * histogram kanału G,
    * histogram kanału B.
5. Wyświetlenie obrazu i histogramów w oknie Matplotlib.

## Algorytm
Ocenia trzy parametry:

1. **Ekspozycja**
* Sprawdza czy średnia wartość pikseli mieści się w przedziale 0.25-0.75.
2. **Kontrast**
* Sprawdza rozrzut wartości pikseli.
* < 0.12 - niski kontrast.
* \> 0.23 - wysoki kontrast. 
3. **Clipping**
* Procent pikseli w skrajnych 2% częściach histogramu.
* Jeśli udział przekracza 5% wszystkich pikseli, to dochodzi do clippingu.

