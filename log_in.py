import json
import shutil
import os
import osmnx
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def refresh_map(map_ll):
    """
    Перезагрузка карты
    """
    map_params = {
        "ll": f'{map_ll[0]},{map_ll[1]}',
        "l": 'map',
        'z': 16,
    }
    response = make_request('https://static-maps.yandex.ru/1.x/', params=map_params)
    if not response:
        print('Ошибка: не могу получить карту')
        return
    with open('static/img/tmp.jpg', mode='wb') as tmp:
        tmp.write(response.content)


def search(name):
    """
    Поиск по карте
    """
    x, y = geo_locate(name)
    if x == -1 or y == -1:
        return
    map_ll = [x, y]
    refresh_map(map_ll)
    shutil.rmtree(os.path.abspath('cache'))


def geo_locate(name):
    """
    Ищем локацию по названию OSM-кой
    Проверка на расположение с помощью Яндекс.карт
    """
    try:
        coords = osmnx.geocode(name)
        params = {
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'geocode': str(coords[1]) + ' ' + str(coords[0]),
            'format': 'json'
        }
        response = make_request('http://geocode-maps.yandex.ru/1.x/', params=params)
    except osmnx._errors.InsufficientResponseError:
        print(f'Ошибка: не могу получить место с названием "{name}"')
        return -1, -1

    with open('result.json', 'w', encoding='utf8') as file:
        text = response.json()
        file.write(json.dumps(text, ensure_ascii=False))

    geo_objects = response.json()['response']["GeoObjectCollection"]["featureMember"]
    if not geo_objects:
        print('Ошибка: не могу получить место')
        return -1, -1

    correct_geo_objects = []

    for geo_object in geo_objects:
        try:
            if (geo_object["GeoObject"]['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']
            ['AdministrativeArea']['AdministrativeAreaName'] == 'Москва'):
                correct_geo_objects.append(geo_object)
        except KeyError:
            pass

    if not correct_geo_objects:
        print('Ошибка: место находится не в Москве')
        return -1, -1

    return [coords[1], coords[0]]


def make_request(*args, **kwargs):
    """
    Собираем запрос
    """
    session = requests.Session()
    retry = Retry(total=100, connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session.get(*args, **kwargs)


if __name__ == '__main__':
    search('Нескучный сад')
