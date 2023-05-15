from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
import pytz
from datetime import datetime, date
from .forms import PersonasForm, ViajesForm, VehiculosForm
from django.contrib import messages
from django.db.models import Sum, Count, Avg, CharField, Value, F, Q, Max
from .choices import categorias_puntuacion, estados_viajes
from .templatetags.filters import ViajesFilter, MensajesFilter, UsuarioviajesopinionesFilter

from .models import Personas, Viajes, Vehiculos, Opiniones, Plazas, Mensajes, Localizaciones

# Create your views here.
def v_ejecuciones(request):
    '''Localizaciones.objects.bulk_create([
        Localizaciones(id_provincia=33, provincia='Asturias'),
        Localizaciones(id_provincia=5, provincia='Ávila'),
        Localizaciones(id_provincia=6, provincia='Badajoz'),
        Localizaciones(id_provincia=7, provincia='Balears, Illes'),
        Localizaciones(id_provincia=8, provincia='Barcelona'),
        Localizaciones(id_provincia=48, provincia='Bizkaia'),
        Localizaciones(id_provincia=9, provincia='Burgos'),
        Localizaciones(id_provincia=10, provincia='Cáceres'),
        Localizaciones(id_provincia=11, provincia='Cádiz'),
        Localizaciones(id_provincia=39, provincia='Cantabria'),
        Localizaciones(id_provincia=12, provincia='Castellón/Castelló'),
        Localizaciones(id_provincia=13, provincia='Ciudad Real'),
        Localizaciones(id_provincia=14, provincia='Córdoba'),
        Localizaciones(id_provincia=15, provincia='Coruña, A'),
        Localizaciones(id_provincia=16, provincia='Cuenca'),
        Localizaciones(id_provincia=20, provincia='Gipuzkoa'),
        Localizaciones(id_provincia=17, provincia='Girona'),
        Localizaciones(id_provincia=18, provincia='Granada'),
        Localizaciones(id_provincia=19, provincia='Guadalajara'),
        Localizaciones(id_provincia=21, provincia='Huelva'),
        Localizaciones(id_provincia=22, provincia='Huesca'),
        Localizaciones(id_provincia=23, provincia='Jaén'),
        Localizaciones(id_provincia=24, provincia='León'),
        Localizaciones(id_provincia=25, provincia='Lleida'),
        Localizaciones(id_provincia=27, provincia='Lugo'),
        Localizaciones(id_provincia=28, provincia='Madrid'),
        Localizaciones(id_provincia=29, provincia='Málaga'),
        Localizaciones(id_provincia=30, provincia='Murcia'),
        Localizaciones(id_provincia=31, provincia='Navarra'),
        Localizaciones(id_provincia=32, provincia='Ourense'),
        Localizaciones(id_provincia=34, provincia='Palencia'),
        Localizaciones(id_provincia=35, provincia='Palmas, Las'),
        Localizaciones(id_provincia=36, provincia='Pontevedra'),
        Localizaciones(id_provincia=26, provincia='Rioja, La'),
        Localizaciones(id_provincia=37, provincia='Salamanca'),
        Localizaciones(id_provincia=38, provincia='Santa Cruz de Tenerife'),
        Localizaciones(id_provincia=40, provincia='Segovia'),
        Localizaciones(id_provincia=41, provincia='Sevilla'),
        Localizaciones(id_provincia=42, provincia='Soria'),
        Localizaciones(id_provincia=43, provincia='Tarragona'),
        Localizaciones(id_provincia=44, provincia='Teruel'),
        Localizaciones(id_provincia=45, provincia='Toledo'),
        Localizaciones(id_provincia=46, provincia='Valencia/València'),
        Localizaciones(id_provincia=47, provincia='Valladolid'),
        Localizaciones(id_provincia=49, provincia='Zamora'),
        Localizaciones(id_provincia=50, provincia='Zaragoza'),
        Localizaciones(id_provincia=51, provincia='Ceuta'),
        Localizaciones(id_provincia=52, provincia='Melilla'),
    ])'''

    return render(request, 'pagina_principal.html')

def v_pagina_principal(request):
    dateNow = timezone.now()
    #timeNow = datetime.time(datetime.now())

    # Se comprueba si se ha introducido el user/pass
    email_input = request.POST.get('txtEmail', False)
    pass_input = request.POST.get('txtPass', False)
    existe_persona = Personas.objects.filter(email=email_input, password=pass_input)

    if not email_input and not pass_input:
        numalert = 1 #Primera vez
        datos_usuario = None
        idP = None
    elif existe_persona:
        numalert = 2  # OK Login
        datos_usuario = Personas.objects.filter(email=email_input, password=pass_input).first()
        idP = datos_usuario.id
    else:
        numalert = 3  # Error Login
        datos_usuario = None
        idP = None

    localizaciones = Localizaciones.objects.all()

    # Se recuperan los 4 próximos viajes
    ##viajesProximos = Viajes.objects.all().order_by('-fecha_ida', '-hora_ida').filter(fecha_ida__gte=dateNow,hora_ida__gte=timeNow)[0:3]
    #viajesProximos = Viajes.objects.all().filter(fechor_ida__gte=dateNow).order_by('fechor_ida')[0:4]
    viajesProximos = Viajes.objects.values('id_persona_id', 'id_persona_id__nombre', 'ciudad_origen'
                                                     , 'ciudad_destino', 'fechor_ida'
                                                     , 'importe_total_asiento',
                                                     'numero_asientos_libres',
                                                     'estado', 'id_persona_id__pref_conversacion',
                                                     'id_persona_id__pref_fumar', 'id_persona_id__imagen') \
        .annotate(count_opiniones=Count('opiniones__mensaje_opinion'), avg_puntuacion=Avg('opiniones__puntuacion')) \
        .filter(fechor_ida__gte=dateNow) \
        .order_by('fechor_ida')[0:4]

    args = {
        'idP': idP,
        'usuario': datos_usuario,
        'localizaciones': localizaciones,
        'viajesProximos': viajesProximos,
        'numAlert': numalert
    }
    return render(request, "pagina_principal.html", args)

def v_buscar_viaje(request, idP):
    datos_usuario = Personas.objects.get(id=idP)
    origen = request.POST.get('inputOrigen')
    destino = request.POST.get('inputDestino')
    fecha = request.POST.get('inputFecha')
    plazas = request.POST.get('inputPlazas')

    localizaciones = Localizaciones.objects.all()

    Usuario_Viajes_Opiniones = Viajes.objects.values('id_persona_id__nombre', 'ciudad_origen'
                                                        , 'ciudad_destino', 'fechor_ida'
                                                        , 'importe_total_asiento',
                                                        'numero_asientos_libres',
                                                        'estado', 'id_persona_id__pref_conversacion',
                                                        'id_persona_id__pref_fumar', 'id_persona_id__imagen')\
        .annotate(count_opiniones=Count('opiniones__mensaje_opinion'), avg_puntuacion=Avg('opiniones__puntuacion'))\
        .filter(ciudad_origen=origen, ciudad_destino=destino, fechor_ida__date=fecha)\
        .order_by('fechor_ida')

    fV = UsuarioviajesopinionesFilter(request.POST, queryset=Usuario_Viajes_Opiniones)
    args = {
        'idP': idP,
        'usuario': datos_usuario,
        'localizaciones': localizaciones,
        'filter': fV,
        'ciudad_origen': origen,
        'ciudad_destino': destino,
        'fecha_viaje': fecha,
        'nro_plazas': plazas
    }

    return render(request, "buscar_viaje.html", args)

def v_nuevo_usuario(request):
    if request.method == "POST":
        form = PersonasForm(request.POST, request.FILES)
        if form.is_valid():
            persona = form.save()
            persona.save()
            messages.success(request, "¡¡¡Usuario creado correctamente!!!.")
            return redirect('n_pagina_principal')
        else:
            #print(form.errors)
            messages.error(request, "¡¡¡ERROR. Usuario no creado!!!.")
            return redirect('n_pagina_principal')
    else:
        form = PersonasForm()
        return render(request, 'nuevo_usuario.html', {'form': form})

def v_listado_usuarios(request):
    usuariosListados = Personas.objects.all()

    args = {"usuarios": usuariosListados}

    return render(request, "listado_usuarios.html", args)

def v_nuevo_viaje(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
        "idP": idP,
        "usuario": datos_usuario
    }

    if request.method == "POST":
        form = ViajesForm(request.POST)
        if form.is_valid():
            viaje = form.save(commit=False)
            viaje.id_persona = Personas.objects.get(id=idP)
            viaje.importe_comision_asiento = viaje.importe_conductor_asiento/10
            viaje.importe_total_asiento = viaje.importe_comision_asiento + viaje.importe_conductor_asiento
            viaje.fechor_ida = datetime.combine(viaje.fecha_ida, viaje.hora_ida)
            viaje.save()
            #Insertamos la plaza del conductor
            plaza_conductor = Plazas(id_persona=datos_usuario, id_viaje=viaje, flg_conductor=True, estado=2)
            plaza_conductor.save()
            messages.success(request, "¡¡¡Viaje publicado correctamente!!!.")
            return redirect('n_pagina_principal')
        else:
            messages.error(request, "¡¡¡ERROR. Viaje no publicado!!!.")
            return redirect('n_pagina_principal')
    else:
        form = ViajesForm()
        args.update({'form': form})
        return render(request, 'nuevo_viaje.html', args)

def v_listado_viajes(request):
    viajesListados = Viajes.objects.all()

    args = {"viajes": viajesListados}

    return render(request, "listado_viajes.html", args)

def v_menu_usuario(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
            "idP": idP,
            "usuario": datos_usuario
            }
    if request.method == "POST":
        form = PersonasForm(request.POST, request.FILES, instance=datos_usuario)
        if form.is_valid():
            persona = form.save()
            persona.save()
            messages.success(request, "¡¡¡Datos de Usuario actualizados correctamente!!!")
            return redirect('n_menu_usuario', idP=idP)
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!!")
            return redirect('n_menu_usuario', idP=idP)
    else:
        # Se crea un form con la información del usuario logueado
        form = PersonasForm(instance=datos_usuario)
        args.update({"form": form})
        return render(request, 'menu_usuario.html', args)

def v_menu_usuario_perfil(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
            "idP": idP,
            "usuario": datos_usuario
            }
    if request.method == "POST":
        form = PersonasForm(request.POST, request.FILES, instance=datos_usuario)
        if form.is_valid():
            persona = form.save()
            persona.save()
            messages.success(request, "¡¡¡Datos de Usuario actualizados correctamente!!!")
            return redirect('n_menu_usuario_perfil', idP=idP)
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!!")
            return redirect('n_menu_usuario_perfil', idP=idP)
    else:
        # Se crea un form con la información del usuario logueado
        form = PersonasForm(instance=datos_usuario)
        args.update({"form": form})
        return render(request, 'menu_usuario_perfil.html', args)

def v_menu_usuario_coches(request, idP):
    usuario = Personas.objects.get(id=idP)
    try:
        vehiculos = Vehiculos.objects.all().filter(id_persona=usuario)
    except Vehiculos.DoesNotExist:
        vehiculos = None

    args = {
            "idP": idP,
            "usuario": usuario,
            "vehiculos": vehiculos
            }

    if request.method == "POST":
        form = VehiculosForm(request.POST, request.FILES)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.id_persona = usuario
            vehiculo.save()
            messages.success(request, "¡¡¡Vehiculo registrado correctamente!!!")
            return redirect('n_menu_usuario_coches', idP=idP)
        else:
            messages.error(request, "¡¡¡ERROR. El vehículo no se ha podido registrar!!!")
            return redirect('n_menu_usuario_coches', idP=idP)
    else:
        # Se crea un form con la información del usuario logueado
        form = VehiculosForm()
        args.update({"form": form})
        return render(request, 'menu_usuario_coches.html', args)

def v_menu_usuario_coches_eliminar(request, idP, idVe):
    vehiculo=Vehiculos.objects.get(id=idVe)
    vehiculo.delete()

    return redirect('n_menu_usuario_coches', idP=idP)

def v_menu_usuario_coches_editar(request, idP, idVe):
    vehiculo=Vehiculos.objects.get(id=idVe)
    args = {
        "idP": idP,
        "vehiculo": vehiculo
    }
    if request.method == "POST":
        form = VehiculosForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            vehiculoform = form.save()
            vehiculoform.save()
            messages.success(request, "¡¡¡Datos de vehiculo actualizados correctamente!!!")
            return redirect('n_menu_usuario_coches', idP=idP)
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!! Prueba de nuevo!!!")
            return redirect('n_menu_usuario_coches', idP=idP)
    else:
        # Se crea un form con la información del usuario logueado
        form = VehiculosForm(instance=vehiculo)
        args.update({"form": form})
        return render(request, 'editar_coche.html', args)

def v_menu_usuario_preferencias(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
        "idP": idP,
        "usuario": datos_usuario
    }
    if request.method == "POST":
        datos_usuario.pref_conversacion = request.POST['pref_conversacion']
        datos_usuario.pref_musica = request.POST['pref_musica']
        datos_usuario.pref_mascota = request.POST['pref_mascota']
        datos_usuario.pref_fumar = request.POST['pref_fumar']
        datos_usuario.pref_comida = request.POST['pref_comida']
        datos_usuario.save()
        messages.success(request, "¡¡¡Preferencias actualizadas correctamente!!!")
        return redirect('n_menu_usuario_preferencias', idP=idP)
    else:
        return render(request, 'menu_usuario_preferencias.html', args)

def v_menu_usuario_opiniones(request, idP):
    usuario = Personas.objects.get(id=idP)
    opiniones_recibidas = Opiniones.objects.all().filter(id_persona_receptor=usuario)
    opiniones_publicadas = Opiniones.objects.all().filter(id_persona_publicador=usuario)

    # Se crea un diccionario con las categorias de opiniones y su valor
    opiniones_cat_dict = dict()
    for x in reversed(range(len(categorias_puntuacion))):  # de 0 a 4 (5 iteraciones)
        categoria = categorias_puntuacion[x][1]
        count_opiniones = opiniones_recibidas.filter(categoria_puntuacion=(x+1)).count()
        opiniones_cat_dict.update({categoria: count_opiniones})

    avg_puntuacion = opiniones_recibidas.aggregate(avg_punt=Avg('puntuacion'))
    total_opiniones = opiniones_recibidas.count()

    args = {
            "idP": idP,
            "usuario": usuario,
            "opiniones_recibidas": opiniones_recibidas,
            "opiniones_publicadas": opiniones_publicadas,
            "avg_puntuacion": avg_puntuacion,
            "total_opiniones": total_opiniones,
            "opiniones_cat_dict": opiniones_cat_dict
    }
    return render(request, 'menu_usuario_opiniones.html', args)

def v_menu_usuario_notificaciones(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
        "idP": idP,
        "usuario": datos_usuario
    }
    if request.method == "POST":
        notif_noticiasofertas_email = request.POST.get('notif_noticiasofertas_email')
        notif_noticiasofertas_sms = request.POST.get('notif_noticiasofertas_sms')
        notif_noticiasofertas = 0
        if(notif_noticiasofertas_email):
            if(notif_noticiasofertas_sms):
                notif_noticiasofertas = 3
            else:
                notif_noticiasofertas = 1
        else:
            if (notif_noticiasofertas_sms):
                notif_noticiasofertas = 2
            else:
                notif_noticiasofertas = 0

        notif_opiniones_email = request.POST.get('notif_opiniones_email')
        notif_opiniones_sms = request.POST.get('notif_opiniones_sms')
        notif_opiniones = 0
        if (notif_opiniones_email):
            if (notif_opiniones_sms):
                notif_opiniones = 3
            else:
                notif_opiniones = 1
        else:
            if (notif_opiniones_sms):
                notif_opiniones = 2
            else:
                notif_opiniones = 0

        notif_reservas_email = request.POST.get('notif_reservas_email')
        notif_reservas_sms = request.POST.get('notif_reservas_sms')
        notif_reservas = 0
        if (notif_reservas_email):
            if (notif_reservas_sms):
                notif_reservas = 3
            else:
                notif_reservas = 1
        else:
            if (notif_reservas_sms):
                notif_reservas = 2
            else:
                notif_reservas = 0

        datos_usuario.notif_noticiasofertas = notif_noticiasofertas
        datos_usuario.notif_opiniones = notif_opiniones
        datos_usuario.notif_reservas = notif_reservas
        datos_usuario.save()
        messages.success(request, "¡¡¡Notificaciones actualizadas correctamente!!!")
        return redirect('n_menu_usuario_notificaciones', idP=idP)
    else:
        return render(request, 'menu_usuario_notificaciones.html', args)

def v_menu_usuario_pagoscobros(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
            "idP": idP,
            "usuario": datos_usuario
            }

    return render(request, 'menu_usuario_pagoscobros.html', args)

def v_menu_usuario_contrasenya(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
        "idP": idP,
        "usuario": datos_usuario
    }
    if request.method == "POST":
        print(request.POST['nueva_password'])
        datos_usuario.password = request.POST['nueva_password']
        datos_usuario.save()
        messages.success(request, "¡¡¡Tu contraseña ha sido actualizada correctamente!!!")
        return redirect('n_menu_usuario_contrasenya', idP=idP)
    else:
        return render(request, 'menu_usuario_contrasenya.html', args)

def v_perfil_publico(request, idP):
    usuario = Personas.objects.get(id=idP)
    try:
        vehiculo = Vehiculos.objects.filter(id_persona=usuario).first()
    except vehiculo.DoesNotExist:
        vehiculo = None

    try:
        viajesConductor = Viajes.objects.all().filter(id_persona=usuario)
    except viajesConductor.DoesNotExist:
        viajesConductor = None

    try:
        reservasPasajero = Plazas.objects.all().filter(id_persona=usuario)
    except reservasPasajero.DoesNotExist:
        reservasPasajero = None

    try:
        opiniones_recibidas = Opiniones.objects.all().filter(id_persona_receptor=usuario)
    except opiniones_recibidas.DoesNotExist:
        opiniones_recibidas = None
    total_viajesConductor = viajesConductor.count()
    total_viajesConductor_Canc = viajesConductor.filter(estado=3).count()
    total_viajesPasajero = reservasPasajero.count()
    total_viajesPasajero_Canc = reservasPasajero.filter(estado=3).count()
    avg_puntuacion = opiniones_recibidas.aggregate(avg_punt=Avg('puntuacion'))
    avg_puntuacion_Conductor = opiniones_recibidas.filter(id_viaje__in = viajesConductor).aggregate(avg_punt=Avg('puntuacion'))
    total_opiniones = opiniones_recibidas.count()

    # Se crea un diccionario con las categorias de opiniones y su valor
    opiniones_cat_dict = dict()
    for x in reversed(range(len(categorias_puntuacion))):  # de 0 a 4 (5 iteraciones)
        categoria = categorias_puntuacion[x][1]
        count_opiniones = opiniones_recibidas.filter(categoria_puntuacion=(x+1)).count()
        opiniones_cat_dict.update({categoria: count_opiniones})

    args = {
        "idP": idP,
        "usuario": usuario,
        "vehiculo": vehiculo,
        "total_viajesConductor": total_viajesConductor,
        "total_viajesConductor_Canc": total_viajesConductor_Canc,
        "total_viajesPasajero": total_viajesPasajero,
        "total_viajesPasajero_Canc": total_viajesPasajero_Canc,
        "avg_puntuacion": avg_puntuacion,
        "avg_puntuacion_Conductor": avg_puntuacion_Conductor,
        "total_opiniones": total_opiniones,
        "opiniones_cat_dict": opiniones_cat_dict
    }

    return render(request, 'perfil_publico.html', args)

def v_mis_viajes(request, idP):
    usuario = Personas.objects.get(id=idP)

    try:
        #reservasPasajero = Plazas.objects.all().filter(id_persona=usuario)
        #viajesPasajero = Viajes.objects.all().filter(id__in=reservasPasajero.values_list('id_viaje').distinct())
        #viajesConductor = Viajes.objects.all().filter(id_persona=usuario)
        #listado_viajes = viajesConductor | viajesPasajero
        #listado_plazas_viajes = Plazas.objects.all().filter(id_viaje__in=listado_viajes)

        plazas = Plazas.objects.all().filter(id_persona=usuario)
        listado_viajes = Viajes.objects.all().filter(id__in=plazas.values_list('id_viaje').distinct())
        listado_plazas_viajes = Plazas.objects.all().filter(id_viaje__in=listado_viajes).order_by('-flg_conductor')

    except plazas.DoesNotExist:
        listado_viajes = None
        listado_plazas_viajes = None

    fV = ViajesFilter(request.GET, queryset=listado_viajes)
    args = {
        "idP": idP,
        "usuario": usuario,
        "filter": fV,
        "listado_plazas_viajes": listado_plazas_viajes
    }

    return render(request, 'mis_viajes.html', args)

def v_mis_mensajes(request, idP):
    usuario = Personas.objects.get(id=idP)

    #listado_conversaciones = Mensajes.objects.all().filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario)).values_list('id_persona_publicador','id_persona_receptor').distinct()
    listado_conversaciones = Mensajes.objects.all().filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario))

    listado_conversaciones = Mensajes.objects.values('id_persona_publicador__nombre', 'id_persona_publicador__apellido1', 'id_persona_publicador__id', 'id_persona_publicador__imagen'
                                                        , 'id_persona_receptor__nombre', 'id_persona_receptor__apellido1', 'id_persona_receptor__id', 'id_persona_receptor__imagen'
                                                        )\
        .annotate(max_fec_created=Max('fec_created'))\
        .filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario))
    print(listado_conversaciones.count())
    fM = MensajesFilter(request.GET, queryset=listado_conversaciones)

    args = {
            "idP": idP,
            "usuario": usuario,
            "filter": fM
            }

    return render(request, "mis_mensajes.html", args)


def v_conversacion(request, idP, idPc):
    usuario = Personas.objects.get(id=idP)
    usuario_receptor = Personas.objects.get(id=idPc)
    listado_mensajes = Mensajes.objects.filter(Q(id_persona_publicador=usuario, id_persona_receptor=usuario_receptor) | Q(id_persona_publicador=usuario_receptor, id_persona_receptor=usuario)).order_by('fec_created')
    args = {
            "idP": idP,
            "usuario": usuario,
            "usuario_receptor": usuario_receptor,
            "listado_mensajes": listado_mensajes
            }
    if request.method == "POST":
        # Insertamos el mensaje
        mensaje = request.POST.get('mensaje', False)
        nuevo_mensaje = Mensajes(id_persona_publicador=usuario, id_persona_receptor=usuario_receptor, flg_leido=False, mensaje=mensaje)
        nuevo_mensaje.save()
        return render(request, "conversacion.html", args)
    else:
        return render(request, "conversacion.html", args)

def v_opiniones_recibidas_main(request, idP):
    usuario = Personas.objects.get(id=idP)

    try:
        opiniones_recibidas = Opiniones.objects.all().filter(id_persona_receptor=usuario)
    except opiniones_recibidas.DoesNotExist:
        opiniones_recibidas = None

    avg_puntuacion = opiniones_recibidas.aggregate(avg_punt=Avg('puntuacion'))
    total_opiniones = opiniones_recibidas.count()

    # Se crea un diccionario con las categorias de opiniones y su valor
    opiniones_cat_dict = dict()
    for x in reversed(range(len(categorias_puntuacion))):  # de 0 a 4 (5 iteraciones)
        categoria = categorias_puntuacion[x][1]
        count_opiniones = opiniones_recibidas.filter(categoria_puntuacion=(x+1)).count()
        opiniones_cat_dict.update({categoria: count_opiniones})

    args = {
        "idP": idP,
        "usuario": usuario,
        "avg_puntuacion": avg_puntuacion,
        "total_opiniones": total_opiniones,
        "opiniones_recibidas": opiniones_recibidas,
        "opiniones_cat_dict": opiniones_cat_dict
    }

    return render(request, 'opiniones_recibidas_main.html', args)



def main(request):
    email_input = request.POST.get('txtEmail', False)
    pass_input = request.POST.get('txtPass', False)

    existe_persona = Personas.objects.filter(email=email_input, password=pass_input)

    if existe_persona:
        numalert = 2  #OK Login
        datos_usuario = Personas.objects.get(email=email_input, password=pass_input)
        return render(request, "main.html", {'usuario':datos_usuario, 'numAlert':numalert})
    else:
        numalert = 1 #Error Login
        return render(request, "main.html", {'numAlert':numalert})

def search_journey(request):
    origen_input = request.POST.get('Origen')
    destino_input = request.POST.get('Destino')
    fecha_input = request.POST.get('Fecha')

    viajesListados = Viajes.objects.filter(ciudad_origen=origen_input, ciudad_destino=destino_input, fecha_ida=fecha_input).order_by('fecha_ida')

    datos = {
        'viajes':viajesListados
    }

    return render(request, "main.html", datos)

def v_nuevo_usuario2(request):
    return render(request, "user_register.html", {})

def v_nuevo_viaje2(request, idP):
    return render(request, "journey_register.html", {'ID_Persona':idP})

def adm_perfil(request):
    return render(request, "adm_datospersonales.html", {})

def guardar_usuario(request):
    Email_input = request.POST['txtEmail']
    Password_input = request.POST['txtPass']
    nombre_input = request.POST['txtNombre']
    Apellido1_input = request.POST['txtApe1']
    Apellido2_input = request.POST['txtApe2']
    FechaNacimiento_input = request.POST['datFechaNac']
    TipoDoc_input = request.POST['txtTipoDoc']
    NumeroDoc_input = request.POST['numDoc']
    Telefono_input = request.POST['numTelefono']
    Genero_input = request.POST['txtGenero']
    ruta_foto_input = request.POST['userImg']

    usuario = Personas.objects.create(
        nombre = nombre_input,
        apellido1 = Apellido1_input,
        apellido2 = Apellido2_input,
        fec_nacimiento = FechaNacimiento_input,
        tipo_documento = TipoDoc_input,
        numero_documento = NumeroDoc_input,
        email = Email_input,
        password = Password_input,
        numero_telefono = Telefono_input,
        genero = Genero_input,
        ruta_foto = ruta_foto_input
    )

    numalert = 3  #OK Nuevo usuario creado
    datos_usuario = Personas.objects.get(email=Email_input, password=Password_input)

    return render(request, "home.html", {'usuario': datos_usuario, 'numAlert': numalert})

def guardar_viaje(request):
    idP_input = request.POST['numIdP']
    ciudadO_input = request.POST['txtCiudadO']
    ciudadD_input = request.POST['txtCiudadD']
    idaVuelta_input = request.POST['flgIdaVuelta']
    fechaIda_input = request.POST['datFechaIda']
    fechaVuelta_input = request.POST['datFechaVuelta']
    numeroAsientos_input = request.POST['numAsientos']
    importeConductorAsiento_input = int(request.POST['numImporte'])
    horaIda_input = request.POST['timHoraIda']
    horaVuelta_input = request.POST['timHoraVuelta']

    flg_solicitado = False
    flg_reservado = False
    flg_cancelado = False
    flg_incidencia = False
    numero_asientos_libres = numeroAsientos_input
    importe_comision_asiento = importeConductorAsiento_input * 0.1
    importe_total_asiento = importe_comision_asiento + importeConductorAsiento_input

    viaje = Viajes.objects.create(
        id_persona = idP_input,
        ciudad_origen = ciudadO_input,
        ciudad_destino = ciudadD_input,
        flg_ida_vuelta = idaVuelta_input,
        fecha_ida = fechaIda_input,
        fecha_vuelta = fechaVuelta_input,
        numero_asientos_viaje = numeroAsientos_input,
        flg_solicitado = flg_solicitado,
        flg_reservado = flg_reservado,
        flg_cancelado = flg_cancelado,
        flg_incidencia = flg_incidencia,
        importe_total_asiento = importe_total_asiento,
        importe_comision_asiento = importe_comision_asiento,
        importe_conductor_asiento = importeConductorAsiento_input,
        numero_asientos_libres = numero_asientos_libres,
        hora_ida = horaIda_input,
        hora_vuelta = horaVuelta_input
    )

    numalert = 4  # OK viaje nuevo publicado

    return render(request, "home.html", {'numAlert': numalert})



def panel_nuevo_vehiculo(request, idP):
    return render(request, "vehicle_register.html", {'ID_Persona':idP})

def guardar_vehiculo(request):
    idP_input = request.POST['numIdP']
    tipoVehiculo_input = request.POST['txtTipoVehiculo']
    marca_input = request.POST['txtMarca']
    modelo_input = request.POST['txtModelo']
    color_input = request.POST['txtColor']
    anosAnt_input = request.POST['numAnosAnt']
    numeroAsientos_input = request.POST['numAsientos']
    flagFumador_input = request.POST['flgFumador']
    flagMascotas_input = request.POST['flgMascotas']

    vehiculo = Vehiculos.objects.create(
        id_persona = idP_input,
        tipo_vehiculo = tipoVehiculo_input,
        marca = marca_input,
        modelo = modelo_input,
        color = color_input,
        años_antiguedad = anosAnt_input,
        numero_asientos = numeroAsientos_input,
        flag_acepta_fumador = flagFumador_input,
        flag_acepta_mascota = flagMascotas_input
    )

    return redirect('/prueba_insert/')


def prueba_insert(request):
    return render(request, "prueba_insert.html", {'ID_Persona':'111','ID_Viaje':'222','ID_Vehiculo':'333'})

def panel_mi_perfil(request):
    return render(request, "index.html", {})