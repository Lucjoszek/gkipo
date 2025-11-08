import io
import urllib.request
import http.client
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
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


def display_image(image: Image.Image,
                  title: str = "",
                  axis_enabled: bool = True,
                  colormap: str | None = None,
                  scale: float = 1.0,
                  rotate: float = 0.0) -> np.ndarray:
    """
    Wyświetla obraz z opcjonalnymi modyfikacjami i zwraca tablicę NumPy.

    :param image: Obraz otwarty przez PIL.Image
    :param title: Tytuł
    :param axis_enabled: Czy wyświetlać osie
    :param colormap: Nazwa mapy kolorów
    :param scale: Współczynnik skali
    :param rotate: Obrót w stopniach (dodatnie = w lewo)
    :return: Tablica Numpy obrazu
    :rtype: np.ndarray
    """

    # Skalowanie
    if scale != 1.0:
        width, height = image.size
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size)

    # Obrót
    if rotate != 0.0:
        image = image.rotate(rotate, expand=True)

    # Grayscale (jeśli wybrano 'gray')
    if colormap == 'gray':
        image = ImageOps.grayscale(image)

    # Konwersja na NumPy
    img_np = np.asarray(image)

    # Wyświetlanie obrazu
    if not axis_enabled:
        plt.axis('off')

    plt.title(title)
    imgplot = plt.imshow(img_np)

    if colormap:
        imgplot.set_cmap(colormap)

    plt.show()

    return img_np


if __name__ == '__main__':
    # Pobranie obrazu
    img_resp = get_image_from_web(
        'https://cdn.pixabay.com/photo/2019/12/05/14/04/animal-4675229_1280.jpg'
    )

    if img_resp is not None:
        img_data = io.BytesIO(img_resp.read())

        # Obraz 1 – oryginalny RGB
        img_rgb = Image.open(img_data)
        img_rgb_np = display_image(
            img_rgb,
            title="Oryginalny obraz RGB",
            axis_enabled=False
        )

        # Obraz 2 – Zmodyfikowany (grayscale, resize 50%, obrót 90°)
        img_mod = Image.open(img_data)
        img_mod_np = display_image(
            img_mod,
            title="Zmodyfikowany obraz",
            axis_enabled=False,
            colormap='gray',
            scale=0.5,
            rotate=-90
        )

        # Wyświetlenie informacji o macierzach obrazów
        print('Macierz domyślnego obrazu:\n', img_rgb_np, '\nRozmiar:', img_rgb_np.shape, '\n')
        print('Macierz zmodyfikowanego obrazu:\n', img_mod_np, '\nRozmiar:', img_mod_np.shape)
