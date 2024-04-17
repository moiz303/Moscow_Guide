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
    with open('templates/tmp.png', mode='wb') as tmp:
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


def geo_locate(name):
    """
    Локация по имени и проверка на расположение
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

    for geo_object in geo_objects:
        if (geo_object["GeoObject"]['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['CountryName']
                != 'Россия'):
            geo_objects.remove(geo_object)

    if not geo_objects:
        print('Ошибка: место находится не в России')
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


if __name__ == '__main__':
    search('Московский Кремль')
