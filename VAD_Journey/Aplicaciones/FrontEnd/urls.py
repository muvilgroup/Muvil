from django.urls import path
from Aplicaciones.FrontEnd.views import *
from django.conf import settings #add this for images
from django.conf.urls.static import static #add this for images

urlpatterns = [
    path('', v_pagina_principal, name='n_pagina_principal'),
    path('buscar_viaje/<int:idP>', v_buscar_viaje, name='n_buscar_viaje'),
    path('nuevo_usuario/', v_nuevo_usuario, name='n_nuevo_usuario'),
    path('listado_usuarios/', v_listado_usuarios, name='n_listado_usuarios'),
    path('nuevo_viaje/<int:idP>', v_nuevo_viaje, name='n_nuevo_viaje'),
    path('listado_viajes/', v_listado_viajes, name='n_listado_viajes'),
    path('menu_usuario/<int:idP>', v_menu_usuario, name='n_menu_usuario'),
    path('menu_usuario/miperfil/<int:idP>', v_menu_usuario_perfil, name='n_menu_usuario_perfil'),
    path('menu_usuario/miscoches/<int:idP>', v_menu_usuario_coches, name='n_menu_usuario_coches'),
    path('menu_usuario/preferencias/<int:idP>', v_menu_usuario_preferencias, name='n_menu_usuario_preferencias'),
    path('menu_usuario/opiniones/<int:idP>', v_menu_usuario_opiniones, name='n_menu_usuario_opiniones'),
    path('menu_usuario/notificaciones/<int:idP>', v_menu_usuario_notificaciones, name='n_menu_usuario_notificaciones'),
    path('menu_usuario/pagoscobros/<int:idP>', v_menu_usuario_pagoscobros, name='n_menu_usuario_pagoscobros'),
    path('menu_usuario/contraseña/<int:idP>', v_menu_usuario_contrasenya, name='n_menu_usuario_contrasenya'),
    path('menu_usuario/miscoches/<int:idP>/eliminar/<int:idVe>', v_menu_usuario_coches_eliminar, name='n_menu_usuario_coches_eliminar'),
    path('menu_usuario/miscoches/<int:idP>/editar/<int:idVe>', v_menu_usuario_coches_editar, name='n_menu_usuario_coches_editar'),
    path('perfil_publico/<int:idP>', v_perfil_publico, name='n_perfil_publico'),

    path('nuevo_usuario2/', v_nuevo_usuario2),
    path('nuevo_viaje2/<int:idP>', v_nuevo_viaje2),
    path('save_user/', guardar_usuario),
    path('save_journey/', guardar_viaje),
    path('vehicle_register/<int:idP>', panel_nuevo_vehiculo),
    path('save_vehicle/', guardar_vehiculo),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
