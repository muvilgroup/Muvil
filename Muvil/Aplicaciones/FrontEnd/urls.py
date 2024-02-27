from django.urls import path, re_path
from Aplicaciones.FrontEnd.views import *
from django.conf import settings #add this for images
from django.conf.urls.static import static #add this for images


urlpatterns = [
    path('', v_pagina_principal, name='n_pagina_principal'),
    path('registro_usuario/', Vregistrousuario.as_view(), name='n_registro_usuario'),
    path('activar/<uidb64>/<token>', v_activar, name='n_activar'),
    path("resetear_contrasenya/", v_resetear_contrasenya, name="n_resetear_contrasenya"),
    path('reset/<uidb64>/<token>', v_confirmacion_reset, name='n_confirmacion_reset'),
    path('social/signup/', v_signup_redirect, name='n_signup_redirect'),
    path('import_export/', v_import_export, name='n_import_export'),
    path('buscar_viaje/', v_buscar_viaje, name='n_buscar_viaje'),
    path('nuevo_usuario/', v_nuevo_usuario, name='n_nuevo_usuario'),
    path('listado_usuarios/', v_listado_usuarios, name='n_listado_usuarios'),
    path('nuevo_viaje/', v_nuevo_viaje, name='n_nuevo_viaje'),
    path('listado_viajes/', v_listado_viajes, name='n_listado_viajes'),
    path('menu_usuario/miperfil/', v_menu_usuario_perfil, name='n_menu_usuario_perfil'),
    path('menu_usuario/miscoches/', v_menu_usuario_coches, name='n_menu_usuario_coches'),
    path('menu_usuario/preferencias/', v_menu_usuario_preferencias, name='n_menu_usuario_preferencias'),
    path('menu_usuario/micaparazon/', v_menu_usuario_caparazon, name='n_menu_usuario_caparazon'),
    path('menu_usuario/opiniones/', v_menu_usuario_opiniones, name='n_menu_usuario_opiniones'),
    path('menu_usuario/notificaciones/', v_menu_usuario_notificaciones, name='n_menu_usuario_notificaciones'),
    path('menu_usuario/pagoscobros/', v_menu_usuario_pagoscobros, name='n_menu_usuario_pagoscobros'),
    path('menu_usuario/contraseña/', v_menu_usuario_contrasenya, name='n_menu_usuario_contrasenya'),
    path('menu_usuario/miscoches/eliminar/<int:idVe>', v_menu_usuario_coches_eliminar, name='n_menu_usuario_coches_eliminar'),
    path('menu_usuario/miscoches/editar/<int:idVe>', v_menu_usuario_coches_editar, name='n_menu_usuario_coches_editar'),
    path('perfil_publico/<int:idP>', v_perfil_publico, name='n_perfil_publico'),
    path('mis_viajes/', v_mis_viajes, name='n_mis_viajes'),
    path('mis_mensajes/', v_mis_mensajes, name='n_mis_mensajes'),
    path('conversacion/<int:idPc>', v_conversacion, name='n_conversacion'),
    path('opiniones_recibidas/<int:idPr>', v_opiniones_recibidas_main, name='n_opiniones_recibidas_main'),
    path('detalles_viaje/<int:idV>', v_detalles_viaje, name='n_detalles_viaje'),
    path('cancelar_viaje/<int:idV>', v_cancelar_viaje, name='n_cancelar_viaje'),
    path('reservar_plaza/<int:idV>', v_reservar_plaza, name='n_reservar_plaza'),
    path('aceptar_pasajero/<int:idV>-<int:idPl>', v_aceptar_pasajero, name='n_aceptar_pasajero'),
    path('rechazar_pasajero/<int:idV>-<int:idPl>', v_rechazar_pasajero, name='n_rechazar_pasajero'),
    path('cancelar_reserva/<int:idV>-<int:idPl>', v_cancelar_reserva, name='n_cancelar_reserva'),
    path('nueva_opinion/<int:idV>-<int:idPr>-<int:idO>', v_nueva_opinion, name='n_nueva_opinion'),
    path('contacto/', v_contacto, name='n_contacto'),
    path('pasarela_pago/', v_pasarela_pago, name='n_pasarela_pago'),
    #path('enviar_whatsapp/', v_enviar_whatsapp, name='n_enviar_whatsapp'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
