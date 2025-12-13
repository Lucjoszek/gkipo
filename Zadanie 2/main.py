import io
import urllib.request
import http.client
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def get_image_from_web(url: str) -> http.client.HTTPResponse | None:
    """
    Pobiera obraz z internetu jako HTTPResponse.

    :param url: URL
    :return: Obraz jako HTTPResponse
    :rtype: http.client.HTTPResponse
    """
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0'})  # `headers` jest potrzebny, aby uniknąć błędu 403.
    try:
        return urllib.request.urlopen(req)
    except Exception as err:
        print('Error loading image:', err)
        return None


def image_quality_check(img_np: np.ndarray) -> dict:
    """
    Ocena jakości obrazu na podstawie histogramu.

    :param img_np: Obraz w postaci tablicy NumPy
    :return: Słownik z wynikami
    :rtype: dict
    """

    bits: int = np.iinfo(img_np.dtype).bits  # Odczyt liczby bitów
    max_bits_range: int = 2 ** bits - 1  # Zakres bitów

    # Spłaszczenie tablicy do 1D i normalizacja do zakresu 0.0-1.0
    pixels = img_np.ravel().astype(float)
    pixels_norm = pixels / max_bits_range
    total_pixels = pixels.size

    # Progi
    THRESHOLD_SHADOWS = 0.02  # Cienie
    THRESHOLD_HIGHLIGHTS = 0.98  # Światła
    THRESHOLD_DARK = 0.25  # Niedoświetlenie
    THRESHOLD_BRIGHT = 0.75  # Prześwietlenie

    # Obliczenia statystyczne
    mean_val = np.mean(pixels_norm)  # Średnia jasność
    std_dev = np.std(pixels_norm)  # Odchylenie standardowe (kontrast)

    # Analiza clippingu
    shadows_clip_ratio = np.sum(pixels_norm <= THRESHOLD_SHADOWS) / total_pixels
    highlights_clip_ratio = np.sum(pixels_norm >= THRESHOLD_HIGHLIGHTS) / total_pixels

    exposure: str
    contrast: str
    shadows_clip: str
    highlights_clip: str

    # Ocena ekspozycji
    if mean_val < THRESHOLD_DARK:
        exposure = 'Zbyt ciemny'
    elif mean_val > THRESHOLD_BRIGHT:
        exposure = 'Zbyt jasny'
    else:
        exposure = 'Ekspozycja umiarkowana'

    # Ocena kontrastu
    if std_dev < 0.12:
        contrast = 'Niski kontrast'
    elif std_dev > 0.23:
        contrast = 'Wysoki kontrast'
    else:
        contrast = 'Kontrast umiarkowany'

    # Ocena clipping cieni
    if shadows_clip_ratio > 0.05:
        shadows_clip = 'Clipping cieni'
    else:
        shadows_clip = 'Brak clippingu cieni'

    # Clipping świateł
    if highlights_clip_ratio > 0.05:
        highlights_clip = 'Clipping świateł'
    else:
        highlights_clip = 'Brak clippingu świateł'

    return {
        'mean_norm': mean_val,
        'std_dev_norm': std_dev,
        'shadows_clip_ratio': shadows_clip_ratio,
        'highlights_clip_ratio': highlights_clip_ratio,
        'exposure': exposure,
        'contrast': contrast,
        'shadows_clip': shadows_clip,
        'highlights_clip': highlights_clip
    }


if __name__ == '__main__':
    # Pobranie obrazu
    img_resp = get_image_from_web(
        'https://cdn.pixabay.com/photo/2019/12/05/14/04/animal-4675229_1280.jpg'
    )

    if img_resp is not None:
        img_data = io.BytesIO(img_resp.read())

        img = Image.open(img_data)
        img_np = np.asarray(img)

        quality_check = image_quality_check(img_np)  # Analiza jakości obrazu

        # Wyświetlenie informacji analizy
        print(f'Średnia jasność (0-1): {quality_check['mean_norm']:.3f}\n'
              f'Kontrast (std dev): {quality_check['std_dev_norm']:.3f}\n'
              f'Ekspozycja: {quality_check['exposure']}\n'
              f'Kontrast: {quality_check['contrast']}\n'
              f'Clipping cieni: {quality_check['shadows_clip']}: {quality_check['shadows_clip_ratio']:.1%}\n'
              f'Clipping świateł: {quality_check['highlights_clip']}: {quality_check['highlights_clip_ratio']:.1%}')

        bits: int = np.iinfo(img_np.dtype).bits  # Odczyt liczby bitów
        bins: int = 2 ** bits  # Liczba koszy histogramu

        r, g, b = img.split()  # Wydobycie kanałów
        r_np = np.asarray(r)
        g_np = np.asarray(g)
        b_np = np.asarray(b)

        # Układ:
        # - obraz po lewej
        # - histogramy po prawej 2x2
        fig, ax = plt.subplot_mosaic([
            ['img', 'all', 'red'],
            ['img', 'green', 'blue']
        ])

        ax['img'].imshow(img_np)
        ax['img'].set_title('Obraz')
        ax['img'].axis('off')

        # Histogram wszystkich kanałów
        ax['all'].hist(img_np.ravel(), bins=bins, color='gray')
        ax['all'].set_title('Histogram wszystkich kanałów')
        ax['all'].set_xlabel('Poziom jasności')
        ax['all'].set_ylabel('Liczba pikseli')

        # Histogram kanału R
        ax['red'].hist(r_np.ravel(), bins=bins, color='red')
        ax['red'].set_title('Histogram kanału R')
        ax['red'].set_xlabel('Poziom jasności')
        ax['red'].set_ylabel('Liczba pikseli')

        # Histogram kanału G
        ax['green'].hist(g_np.ravel(), bins=bins, color='green')
        ax['green'].set_title('Histogram kanału G')
        ax['green'].set_xlabel('Poziom jasności')
        ax['green'].set_ylabel('Liczba pikseli')

        # Histogram kanału B
        ax['blue'].hist(b_np.ravel(), bins=bins, color='blue')
        ax['blue'].set_title('Histogram kanału B')
        ax['blue'].set_xlabel('Poziom jasności')
        ax['blue'].set_ylabel('Liczba pikseli')

        plt.tight_layout()
        plt.show()
