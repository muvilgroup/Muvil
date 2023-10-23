from geopy.geocoders import Nominatim
from geopy.distance import distance
import openrouteservice


class Geolocalizacion():
    def __init__(self):
        self.__geo = Nominatim(user_agent="MUVIL")
        self.__client = openrouteservice.Client(key='5b3ce3597851110001cf6248e9ddd2e474884ff994afc9527d659a58')

    def obtener_direccion(self, input_direccion):
        direccion = self.geo.geocode(input_direccion)

        return direccion

    def obtener_coordenadas(self, input_direccion):
        direccion = self.geo.geocode(input_direccion)

        return direccion.latitude, direccion.longitude

    def calcular_distancia_recta(self, input_direccion1, input_direccion2):
        dir1_lat, dir1_long = self.obtener_coordenadas(input_direccion1)
        dir2_lat, dir2_long = self.obtener_coordenadas(input_direccion2)

        return distance((dir1_lat, dir1_long), (dir2_lat, dir2_long))

    def calcular_parametros_conduccion(self, input_direccion1, input_direccion2):
        dir1_lat, dir1_long = self.obtener_coordenadas(input_direccion1)
        dir2_lat, dir2_long = self.obtener_coordenadas(input_direccion2)

        coords = (dir1_long, dir1_lat), (dir2_long, dir2_lat)

        res = self.client.directions(coords, radiuses=[1500])

        distancia_conduccion = round(res['routes'][0]['summary']['distance']/1000, 1) # KMs
        tiempo_conduccion = int(res['routes'][0]['summary']['duration']/60) # Minutos

        return distancia_conduccion, tiempo_conduccion

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, value):
        self.__geo = value

    @property
    def client(self):
        return self.__client

    @client.setter
    def client(self, value):
        self.__client = value
