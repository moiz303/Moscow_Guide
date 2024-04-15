import pyttsx3
import sys

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def TextSpeech(text_speech: str):
    """
    Озвучиваем текст
    """
    tts = pyttsx3.init()
    tts.say(text_speech)
    tts.runAndWait()


class MainWindow(QMainWindow):
    g_map: QLabel

    # noinspection PyUnresolvedReferences
    def __init__(self):
        super().__init__()
        uic.loadUi('templates/main_window.ui', self)

        self.map_zoom = 15
        self.map_ll = [37.977751, 55.757718]
        self.map_l = 'map'

        self.refresh_map()

    def refresh_map(self):
        """
        Перезагрузка карты
        """
        map_params = {
            "ll": f'{self.map_ll[0]},{self.map_ll[1]}',
            "l": self.map_l,
            'z': self.map_zoom,
        }
        response = make_request('https://static-maps.yandex.ru/1.x/', params=map_params)
        if not response:
            print('Ошибка: не могу получить карту')
            return
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')

        self.g_map.setPixmap(pixmap)

    def search(self):
        """
        Поиск по карте
        """
        x, y = geo_locate('Московский кремль')
        if x == -1 or y == -1:
            return
        self.map_ll = [x, y]
        self.refresh_map()


def geo_locate(name):
    """
    Локация по имени
    """
    params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': name,
        'format': 'json'
    }
    response = make_request('http://geocode-maps.yandex.ru/1.x/', params=params)
    if not response:
        print(f'Ошибка: не могу получить место с названием {name}')
        return -1, -1
    geo_objects = response.json()['response']["GeoObjectCollection"]["featureMember"]
    if not geo_objects:
        print('Ошибка: не могу получить место')
        return -1, -1
    return list(map(float, geo_objects[0]["GeoObject"]["Point"]["pos"].split()))


def make_request(*args, **kwargs):
    """
    Собираем запрос
    """
    session = requests.Session()
    retry = Retry(total=10, connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session.get(*args, **kwargs)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
