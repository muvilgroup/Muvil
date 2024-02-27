from apscheduler.schedulers.background import BackgroundScheduler
from .background_tasks import actualizar_estado_viajes, eliminar_usuarios_caducados


def start():
    ###################################################################################################################
    # Como activar tareas automáticas:
    # 1.- crear las tareas en el background_tasks.py con la acción que se quiere programar
    # 2.- crear un objeto scheduler como una instancia del BackgroundScheduler()
    # 2.- importar la tarea del paso 1 en este script y añadir el job con scheduler.add_job(nombre_job)
    # 3.- iniciar el disparador de tareas: scheduler.start
    ###################################################################################################################

    scheduler = BackgroundScheduler()
    scheduler.add_job(actualizar_estado_viajes, 'interval', seconds=2) # 15 minutos
    #scheduler.add_job(eliminar_usuarios_caducados, 'interval', seconds=100000000000000)

    scheduler.start()

