from django.urls import path
from Aplicaciones.FrontEnd.views import v_pagina_principal, v_buscar_viaje, v_nuevo_usuario, v_nuevo_viaje, v_menu_usuario, guardar_usuario, panel_nuevo_vehiculo, guardar_vehiculo, guardar_viaje

urlpatterns = [
    path('', v_pagina_principal),
    path('buscar_viaje/<int:idP>', v_buscar_viaje),
    path('nuevo_usuario/', v_nuevo_usuario),
    path('nuevo_viaje/<int:idP>', v_nuevo_viaje),
    path('menu_usuario/<int:idP>', v_menu_usuario),
    path('save_user/', guardar_usuario),
    path('save_journey/', guardar_viaje),
    path('vehicle_register/<int:idP>', panel_nuevo_vehiculo),
    path('save_vehicle/', guardar_vehiculo),
]

'''
## Antiguos
path('main/', main),
path('user_register/', panel_nuevo_usuario),
path('save_user/', guardar_usuario),
path('journey_register/<int:idP>', panel_nuevo_viaje),
path('save_journey/', guardar_viaje),
path('vehicle_register/<int:idP>', panel_nuevo_vehiculo),
path('save_vehicle/', guardar_vehiculo),
path('prueba_insert/', prueba_insert),
path('search_journey/', search_journey),
'''