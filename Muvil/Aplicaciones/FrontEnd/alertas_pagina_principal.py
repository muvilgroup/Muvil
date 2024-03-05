from .models import Plazas, Opiniones, Mensajes
from django.db.models import Q


class AlertasPrincipal():
    def __init__(self, usuario_input=None):
        self.__usuario = usuario_input

    def alert_mensajes_salida(self):
        lista_mensajes = []
        lista_mensajes += [self.alert_plazas_pendiente_aceptar()] if self.alert_plazas_pendiente_aceptar() is not None else []
        lista_mensajes += [self.alert_plaza_aceptada()] if self.alert_plaza_aceptada() is not None else []
        lista_mensajes += [self.alert_plaza_rechazada()] if self.alert_plaza_rechazada() is not None else []
        lista_mensajes += [self.alert_viaje_finalizado()] if self.alert_viaje_finalizado() is not None else []
        lista_mensajes += [self.alert_viaje_cancelado()] if self.alert_viaje_cancelado() is not None else []
        lista_mensajes += [self.alert_mensajes_nuevos()] if self.alert_mensajes_nuevos() is not None else []
        lista_mensajes += [self.alert_opiniones_nuevas()] if self.alert_opiniones_nuevas() is not None else []
        return lista_mensajes

    def alert_plazas_pendiente_aceptar(self):
        '''
            1.- Notificar si hay plazas pendientes de aceptar no vistas
        '''

        criterio_viajes_user = Q(id_viaje__id_persona_id__id_usuario_id=self.usuario.id)
        criterio_plazas_pend = Q(estado=1)
        criterio_plaza_pend_no_vista = Q(fechor_pendiente__gt=self.usuario.last_login)
        plazas_pendientes_aceptar = Plazas.objects.filter(criterio_viajes_user &
                                                          criterio_plazas_pend &
                                                          criterio_plaza_pend_no_vista)
        if plazas_pendientes_aceptar:
            return f"¡ATENCIÓN! Tienes nuevas reservas en alguno de tus viajes.<br>\
                      Puedes verlas en la sección <a class='btn btn-warning fw-bold' href='/mis_viajes'>Mis Viajes</a>"
        else:
            return None

    def alert_plaza_aceptada(self):
        '''
            2.- Notificar si se ha aceptado mi reserva de plaza
        '''

        criterio_plazas_user = Q(id_persona_id__id_usuario_id=self.usuario.id)
        criterio_plazas_conf = Q(estado=2)
        criterio_plaza_conf_no_vista = Q(fechor_confirmado__gt=self.usuario.last_login)
        plazas_aceptadas = Plazas.objects.filter(criterio_plazas_user &
                                                 criterio_plazas_conf &
                                                 criterio_plaza_conf_no_vista)
        if plazas_aceptadas:
            return f"¡GENIAL! Tu reserva ha sido confirmada.<br>\
                      Consulta los detalles del viaje en la sección <a class='btn btn-warning fw-bold boton-3d' \
                      href='/mis_viajes'>Mis Viajes</a>"
        else:
            return None

    def alert_plaza_rechazada(self):
        '''
            3.- Notificar si se ha rechazado mi reserva
        '''

        criterio_plazas_user = Q(id_persona_id__id_usuario_id=self.usuario.id)
        criterio_plazas_rech = Q(estado=3)
        criterio_plaza_rech_no_vista = Q(fechor_rechazado__gt=self.usuario.last_login)
        plazas_rechazadas = Plazas.objects.filter(criterio_plazas_user &
                                                  criterio_plazas_rech &
                                                  criterio_plaza_rech_no_vista)
        if plazas_rechazadas:
            return f"¡VAYA! Tu reserva pendiente ha sido rechazada.<br>\
                     Prueba a reservar en otro de los viajes."
        else:
            return None

    def alert_viaje_finalizado(self):
        '''
            # 4.- Notificar si ha finalizado un viaje en el que fui conductor o pasajero
        '''
        criterio_plazas_user = Q(id_persona_id__id_usuario_id=self.usuario.id)
        criterio_viaje_realizado = Q(id_viaje__estado=2)
        criterio_viaje_realizado_no_visto = Q(id_viaje__fechor_llegada__gt=self.usuario.last_login)
        mis_viajes_finalizados = Plazas.objects.filter(criterio_plazas_user &
                                                   criterio_viaje_realizado &
                                                   criterio_viaje_realizado_no_visto)
        if mis_viajes_finalizados:
            return f"¡Tu viaje ha finalizado! ¿Ha ido todo bien?.<br>\
                     En la sección <a class='btn btn-warning fw-bold boton-3d' href='/mis_viajes'>Mis Viajes</a> \
                     puedes confirmar que todo fue bien y dejar una reseña al conductor/pasajero."
        else:
            return None

    def alert_viaje_cancelado(self):
        '''
            # 5.- Notificar si se ha cancelado mi viaje
        '''
        criterio_plazas_user = Q(id_persona_id__id_usuario_id=self.usuario.id)
        criterio_viaje_canc = Q(id_viaje__estado=3)
        criterio_plaza_canc_no_vista = Q(fechor_cancelado__gt=self.usuario.last_login)
        mis_viajes_cancelados = Plazas.objects.filter(criterio_plazas_user &
                                                      criterio_viaje_canc &
                                                      criterio_plaza_canc_no_vista)
        if mis_viajes_cancelados:
            return f"¡VAYA! Tu viaje ha sido cancelado.<br>\
                      Prueba a reservar en otro de los viajes."
        else:
            return None

    def alert_mensajes_nuevos(self):
        '''
            # 6.- Notificar si hay mensajes nuevos
        '''
        criterio_mensajes_no_leidos = Q(flg_leido=False)
        criterio_mensajes_para_user = Q(id_persona_receptor__id_usuario_id=self.usuario.id)
        mensajes_no_leidos = Mensajes.objects.filter(criterio_mensajes_no_leidos &
                                                     criterio_mensajes_para_user)
        if mensajes_no_leidos:
            return f"¡Tienes mensajes nuevos!<br> \
                     Los puedes leer en la sección <a class='btn btn-warning fw-bold boton-3d'\
                     href='/mis_mensajes'>Mis Mensajes</a>"
        else:
            return None

    def alert_opiniones_nuevas(self):
        '''
            # 7.- Notificar si hay opiniones nuevas
        '''
        criterio_opiniones_no_leidas = Q(flg_leido=False)
        criterio_opiniones_para_user = Q(id_persona_receptor__id_usuario_id=self.usuario.id)
        opiniones_no_leidas = Opiniones.objects.filter(criterio_opiniones_no_leidas &
                                                       criterio_opiniones_para_user)
        if opiniones_no_leidas:
            return f"¡Te han publicado una nueva opinión!<br>La puedes ver en la sección <a class='btn btn-warning \
                     fw-bold boton-3d' href='/menu_usuario/opiniones'>Mis Opiniones</a>"
        else:
            return None

    @property
    def usuario(self):
        return self.__usuario

    @usuario.setter
    def usuario(self, value):
        self.__usuario = value
