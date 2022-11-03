from django.urls import path
from Aplicaciones.FrontEnd.views import v_home, buscar_viaje, panel_mi_perfil, main, panel_nuevo_usuario, guardar_usuario, panel_nuevo_viaje, guardar_viaje, panel_nuevo_vehiculo, guardar_vehiculo, prueba_insert

urlpatterns = [
    path('', v_home),
    path('main/', main),
    path('user_register/', panel_nuevo_usuario),
    path('save_user/', guardar_usuario),
    path('journey_register/<int:idP>', panel_nuevo_viaje),
    path('save_journey/', guardar_viaje),
    path('vehicle_register/<int:idP>', panel_nuevo_vehiculo),
    path('save_vehicle/', guardar_vehiculo),
    path('prueba_insert/', prueba_insert),
    path('search_journey/', buscar_viaje),
    path('mi_profile/', panel_mi_perfil),
]