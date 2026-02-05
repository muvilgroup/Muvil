from .models import Viajes, Plazas
from ..users.models import Usuario
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q, Subquery, OuterRef
from .alertas_pagina_principal import AlertasPrincipal


datetimeNow = timezone.now()

# Tarea para actualizar el estado de los viajes pendientes a REALIZADO cuando la fecha-hora de inicio sea superada
# también se actualizan las plazas a REALIZADO
# REALIZADO implica que el viaje ha finalizado y su estado siguiente será FINALIZADO si fue bien o PROBLEMATICO si alguien tuvo problemas
def actualizar_estado_realizado():
    viajes_realizados = Viajes.objects.filter(estado=1, fechor_ida__lt=datetimeNow)

    #print(viajes_realizados)

    # Para aquellos viajes recién empezados les ponemos estado de la plazas asociadas a Realizado
    if viajes_realizados:
        plazas_realizadas = Plazas.objects.filter(id_viaje__in=viajes_realizados)
        #print(plazas_realizadas)
        plazas_realizadas.update(estado_plaza_viaje=2)

    # Actualizamos el viaje a Realizado
    viajes_realizados.update(estado=4, fechor_realizado=datetimeNow)

def actualizar_estado_finalizado():
    datetimeNowMinus24h = datetimeNow + timezone.timedelta(hours=-24)
    #print(datetimeNowMinus24h)
    # Buscamos los viajes Realizados que lleven mas de 24 horas desde el viaje y su conteo de problemas
    crit1 = Q(
        id_viaje=OuterRef('id'),
        estado_plaza_viaje=4  # Plaza Problematica
    )
    viajes_count_problemas = (Viajes.objects.annotate(count_problematicos=Subquery(
        Plazas.objects.filter(crit1).values('id').annotate(c=Count('*')).values('c'))))
    print(viajes_count_problemas)

    viajes_sin_problemas = viajes_count_problemas.filter(Q(estado=4, fechor_llegada__lt=datetimeNowMinus24h, count_problematicos=None))
    #print(viajes_sin_problemas)

    # Actualizamos las plazas de los viajes sin problemas
    if viajes_sin_problemas:
        plazas_finalizadas = Plazas.objects.filter(id_viaje__in=viajes_sin_problemas)
        #print(plazas_realizadas)
        plazas_realizadas.update(estado_plaza_viaje=3)
    # Actualizamos el viaje a Finalizado
    viajes_sin_problemas.update(estado=2, fechor_finalizado=datetimeNow)

    # Actualizamos a Problematico aquellos viajes con alguna plaza problematica
    viajes_con_problemas = viajes_count_problemas.filter(Q(estado=4, fechor_llegada__lt=datetimeNowMinus24h) & ~Q(count_problematicos=None))
    viajes_con_problemas.update(estado=5, fechor_finalizado=datetimeNow)

# Tarea para eliminar los usuarios a los que le haya caducado el enlace de activación (usuarios no activos)
def eliminar_usuarios_caducados():
    fecha_limite = datetimeNow - datetime.timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
    Usuario.objects.filter(fec_updated__lt=fecha_limite, is_active=False).delete()
