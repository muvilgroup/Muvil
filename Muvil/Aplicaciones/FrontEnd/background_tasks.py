from .models import Viajes
from ..users.models import Usuario
from django.conf import settings
import datetime
from django.utils import timezone

datetimeNow = timezone.now()

# Tarea para actualizar el estado de los viajes pendientes a COMPLETADO cuando la fecha-hora de inicio sea superada
def actualizar_estado_viajes():
    viaje_actualizado = Viajes.objects.filter(estado=1, fechor_ida__lt=datetimeNow).update(estado=2, fechor_realizado=datetimeNow)
    if viaje_actualizado:
        print(f'{datetimeNow.strftime("%D %H:%M:%S")}: actualizar_estado_viajes')

# Tarea para eliminar los usuarios a los que le haya caducado el enlace de activación (usuarios no activos)
def eliminar_usuarios_caducados():
    fecha_limite = datetimeNow - datetime.timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
    Usuario.objects.filter(fec_updated__lt=fecha_limite, is_active=False).delete()
