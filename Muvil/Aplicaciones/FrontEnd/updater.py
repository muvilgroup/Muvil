from apscheduler.schedulers.background import BackgroundScheduler
from .background_tasks import actualizar_estado_viajes, eliminar_usuarios_caducados, prueba_auto


def start():
    scheduler = BackgroundScheduler()
    #scheduler.add_job(actualizar_estado_viajes, 'interval', seconds=900) # 15 minutos
    #scheduler.add_job(eliminar_usuarios_caducados, 'interval', seconds=100000000000000)
    scheduler.add_job(prueba_auto, 'interval', seconds=5)
    scheduler.start()

