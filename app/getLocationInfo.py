import requests
from decimal import *
from geopy.distance import geodesic



def location_info(coords):
	PARAMS = {"apikey": "5b9c5a58-0c50-44d7-8337-c624436041f7", "format": "json", "lang": "ru_RU", "kind": "house", "geocode": coords}
	
	try:
		r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params = PARAMS)
		json_data = r.json()
		address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]

		return address_str
	
	except Exception as e:
		print(e)


def calculate_km(latitude, longitude, latitude2, longitude2):
	distance_in_km = geodesic((latitude, longitude), (latitude2, longitude2)).km
	km = str(distance_in_km).split('.')
	return km[0]


def calculate_distance(latitude, longitude, latitude2, longitude2):
	distance_in_km = geodesic((latitude, longitude), (latitude2, longitude2)).km
	km = str(distance_in_km).split('.')

	distance_in_m = geodesic((latitude, longitude), (latitude2, longitude2)).m
	m = str(distance_in_m).split('.')

	if int(km[0]) < 1:
		return f'{m[0]} м'

	else:
		return f'{km[0]} км'

# x = (calculate_distance(41.369695, 69.202648, 41.369701, 79.202805))
# print(x)

