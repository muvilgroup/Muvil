from datetime import datetime
from .models import Viajes, Vehiculos
from django.db.models import Q


class ValidacionesViajes():
    def __init__(self, persona_input=None, viaje_input=None):
        self.__persona = persona_input
        self.__viaje = viaje_input

    def val_mensajes_salida(self):
        lista_mensajes = []
        lista_mensajes += [self.val_viaje_a_pasado()] if self.val_viaje_a_pasado() is not None else []
        lista_mensajes += [self.val_plazas_maximas_superadas()] if self.val_plazas_maximas_superadas() is not None else []
        lista_mensajes += [self.val_plazas_nulas()] if self.val_plazas_nulas() is not None else []
        lista_mensajes += [self.val_viajes_coincidentes()] if self.val_viajes_coincidentes() is not None else []
        return lista_mensajes

    def val_viaje_a_pasado(self):
        '''
            Validacion de viajes a pasado
        '''
        if self.viaje.fechor_ida < datetime.now():
            return "¡¡¡No se pueden publicar viajes a pasado!!!"
        else:
            return None

    def val_plazas_maximas_superadas(self):
        '''
            Validacion de plazas maximas superadas
        '''
        vehiculo_obj = Vehiculos.objects.get(id=self.viaje.id_vehiculo.id)
        if self.viaje.numero_asientos_viaje > getattr(vehiculo_obj, 'numero_asientos'):
            return "¡¡¡No se pueden ofertar mas plazas de las que el vehiculo acepta!!! Prueba otra vez."
        else:
            return None

    def val_plazas_nulas(self):
        '''
            Validacion de plazas mayor que 0
        '''
        if self.viaje.numero_asientos_viaje <= 0:
            return "¡¡¡No se pueden publicar viajes sin plazas libres!!!"
        else:
            return None

    def val_viajes_coincidentes(self):
        '''
            Validacion viaje nuevo coincidente con otro ya publicado y en estado pendiente
        '''
        criterio = \
            Q(id_persona=self.persona, estado=1, fechor_ida__range=(self.viaje.fechor_ida, self.viaje.fechor_llegada)) \
            | Q(id_persona=self.persona, estado=1, fechor_llegada__range=(self.viaje.fechor_ida, self.viaje.fechor_llegada))
        viajes_coincidentes = Viajes.objects.filter(criterio)
        if viajes_coincidentes:
            return '''¡¡¡ERROR!!! No se pueden tener 2 viajes diferentes en el mismo momento.\n 
                        Tu nuevo viaje coincide en el tiempo con otro que ya tienes publicado, 
                        si quieres publicar este viaje antes debes cancelar el anterior.'''
        else:
            return None

    @property
    def viaje(self):
        return self.__viaje

    @viaje.setter
    def viaje(self, value):
        self.__viaje = value

    @property
    def persona(self):
        return self.__persona

    @persona.setter
    def persona(self, value):
        self.__persona = value
