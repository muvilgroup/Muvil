from django.urls import path
from Aplicaciones.FrontEnd.views import v_pagina_principal, v_buscar_viaje, v_nuevo_usuario, v_listado_usuarios, v_nuevo_viaje, \
    v_listado_viajes, v_menu_usuario_perfil, v_nuevo_usuario2, v_nuevo_viaje2, v_menu_usuario, guardar_usuario, \
    panel_nuevo_vehiculo, guardar_vehiculo, guardar_viaje
from django.conf import settings #add this
from django.conf.urls.static import static #add this

urlpatterns = [
    path('', v_pagina_principal, name='n_pagina_principal'),
    path('buscar_viaje/<int:idP>', v_buscar_viaje),
    path('nuevo_usuario/', v_nuevo_usuario, name='n_nuevo_usuario'),
    path('listado_usuarios/', v_listado_usuarios, name='n_listado_usuarios'),
    path('nuevo_viaje/<int:idP>', v_nuevo_viaje, name='n_nuevo_viaje'),
    path('listado_viajes/', v_listado_viajes, name='n_listado_viajes'),
    path('menu_usuario/<int:idP>', v_menu_usuario, name='n_menu_usuario'),
    path('menu_usuario/miperfil/<int:idP>', v_menu_usuario_perfil, name='n_menu_usuario_perfil'),

    path('nuevo_usuario2/', v_nuevo_usuario2),
    path('nuevo_viaje2/<int:idP>', v_nuevo_viaje2),
    path('save_user/', guardar_usuario),
    path('save_journey/', guardar_viaje),
    path('vehicle_register/<int:idP>', panel_nuevo_vehiculo),
    path('save_vehicle/', guardar_vehiculo),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

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