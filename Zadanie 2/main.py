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
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # `headers` jest potrzebny, aby uniknąć błędu 403.
    try:
        return urllib.request.urlopen(req)
    except Exception as err:
        print('Error loading image:', err)
        return None


def image_quality_check(img_np: np.ndarray) -> str:
    """
    Ocena jakości obrazu na podstawie histogramu.

    :param img_np: Obraz w postaci tablicy NumPy
    :return: Wynik oceny obrazu: "Niedoświetlone" | "Prześwietlone" | "Prawidłowe"
    :rtype: str
    """

    bits: int = np.iinfo(img_np.dtype).bits  # Odczyt liczby bitów
    bins: int = 2 ** bits  # Liczba koszy histogramu

    hist, _ = np.histogram(img_np.ravel(), bins=bins, range=(0, bins - 1))

    # Normalizacja histogramu
    # Każda wartość oznacza procent pikseli o danej jasności
    hist_norm = hist / hist.sum()

    # Obliczenie średniej jasności obrazu
    # jasność * procent wystąpień tej jasności
    brightness_levels = np.arange(bins)
    mean_brightness = np.sum(hist_norm * brightness_levels)

    # Skrajne części obrazu
    # `k` określa, ile najciemniejszych i najjaśniejszych jest analizowane
    # Niech będzie to 1% zakresu
    k = max(1, int(0.01 * bins))

    # Procent pikseli bardzo ciemnych
    left_part = np.sum(hist_norm[:k])

    # Procent pikseli bardzo jasnych
    right_part = np.sum(hist_norm[-k:])

    if mean_brightness < 0.3 * bins and left_part > 0.05:
        return "Niedoświetlone"

    if mean_brightness > 0.7 * bins and right_part > 0.05:
        return "Prześwietlone"

    return "Prawidłowe"


if __name__ == '__main__':
    # Pobranie obrazu
    img_resp = get_image_from_web(
        'https://cdn.pixabay.com/photo/2019/12/05/14/04/animal-4675229_1280.jpg'
    )

    if img_resp is not None:
        img_data = io.BytesIO(img_resp.read())

        img = Image.open(img_data)
        img_np = np.asarray(img)

        bits: int = np.iinfo(img_np.dtype).bits # Odczyt liczby bitów
        bins: int = 2 ** bits # Liczba koszy histogramu

        r, g, b = img.split() # Wydobycie kanałów
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

        print(image_quality_check(img_np))