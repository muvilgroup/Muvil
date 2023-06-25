from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
import pytz
from datetime import datetime, date
from .forms import PersonasForm, ViajesForm, VehiculosForm
from django.contrib import messages
from django.db.models import Sum, Count, Avg, CharField, Value, F, Q, Max, Subquery, OuterRef
from .choices import categorias_puntuacion, estados_viajes
from .templatetags.filters import ViajesFilter, MensajesFilter, UsuarioviajesopinionesFilter
from django.views.generic import View
from django.contrib.auth import login, logout, authenticate

from .models import Personas, Viajes, Vehiculos, Opiniones, Plazas, Mensajes, Localizaciones
from ..users.admin import UserCreationForm as CustomUserCreationForm


# Create your views here.
class Vregistrousuario (View):
    def get(self, request):
        form = CustomUserCreationForm()
        datos = {
            'form': form,
        }
        return render(request,"registro_usuario.html", datos)

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            #username = form.cleaned_data.get('email')
            #messages.success(request, f"Usuario creado correctamente: {username}")
            login(request, usuario)
            #messages.info(request, f"Estas logueado como {username}")
            return redirect('n_nuevo_usuario')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
                print(msg)
            return redirect('n_registro_usuario')

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

    if email_input and pass_input:
        user = authenticate(username=email_input, password=pass_input)
        login(request, user)

    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
        #fk reverso print(request.user.personas_set.all())
    else:
        usuario = None

    numalert = 1
    localizaciones = Localizaciones.objects.all()

    # Se recuperan los 4 próximos viajes
    ##viajesProximos = Viajes.objects.all().order_by('-fecha_ida', '-hora_ida').filter(fecha_ida__gte=dateNow,hora_ida__gte=timeNow)[0:3]
    #viajesProximos = Viajes.objects.all().filter(fechor_ida__gte=dateNow).order_by('fechor_ida')[0:4]
    crit1 = Q(id_persona_receptor=OuterRef('id_persona_id'))
    viajesProximos = Viajes.objects.values('id_persona_id', 'id_persona_id__nombre', 'ciudad_origen'
                                                     ,'id', 'ciudad_destino', 'fechor_ida'
                                                     ,'importe_total_asiento',
                                                     'numero_asientos_libres',
                                                     'estado', 'id_persona_id__pref_conversacion',
                                                     'id_persona_id__pref_fumar', 'id_persona_id__imagen') \
        .annotate(count_opiniones=Subquery(Opiniones.objects.filter(crit1).
                                           values('id_persona_receptor').annotate(c=Count('*')).values('c')),
                  avg_puntuacion=Subquery(Opiniones.objects.filter(crit1).
                                           values('id_persona_receptor').annotate(avg=Avg('puntuacion')).values('avg'))) \
        .filter(Q(fechor_ida__gte=dateNow, numero_asientos_libres__gt=0)) \
        .order_by('fechor_ida')[0:4]
    args = {
        'usuario': usuario,
        'localizaciones': localizaciones,
        'viajesProximos': viajesProximos,
        'numAlert': numalert
    }
    return render(request, "pagina_principal.html", args)

def v_detalles_viaje(request, idV):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    idP = usuario.id

    viaje = Viajes.objects.get(id=idV)
    plazas = Plazas.objects.filter(Q(id_viaje=idV, flg_conductor=False, estado__in=(1, 2))) # plazas pendientes o confirmadas
    flg_reserva_pend_conf = plazas.filter(Q(id_persona=idP)).exists()
    if viaje.id_persona == usuario:
        usuario_conductor = True
    else:
        usuario_conductor = False

    if usuario_conductor:
        opiniones_escritas_x_cond = Opiniones.objects.filter(Q(id_viaje=idV, id_persona_publicador=idP))
        opinion_escrita_a_cond = None
    else:
        opiniones_escritas_x_cond = None
        opinion_escrita_a_cond = Opiniones.objects.filter(Q(id_viaje=idV, id_persona_publicador=idP, id_persona_receptor=viaje.id_persona.id))

    '''
    #Validacion 1: ¿Tiene ya ese usuario una reserva en ese viaje?
    plaza_ya_reservada_pendiente = Plazas.objects.filter(Q(id_viaje=viaje, id_persona=usuario, estado=1)).count()

    if plaza_ya_reservada_pendiente > 0:
        messages.error(request, "¡¡ERROR!! Tienes ya una reserva pendiente para este viaje!! cuando el conductor la acepte o la rechace podrás hacer otra reserva")
    else:
        # 1.- Se inserta la plaza pero como Pendiente
        plaza_reserva = Plazas(id_persona=usuario, id_viaje=viaje, flg_conductor=False, estado=1, fechor_pendiente=datetimeNow)
        plaza_reserva.save()
        messages.success(request, "¡¡¡Ya tienes tu viaje reservado!!! Sólo queda esperar que el conductor acepte!!!")

    return redirect('n_pagina_principal')
    '''
    args = {
        'usuario': usuario,
        'viaje': viaje,
        'plazas': plazas,
        'flg_reserva_pend_conf': flg_reserva_pend_conf,
        'usuario_conductor': usuario_conductor,
        'opiniones_escritas_x_cond': opiniones_escritas_x_cond,
        'opinion_escrita_a_cond': opinion_escrita_a_cond,
    }

    return render(request, "detalles_viaje.html", args)

def v_cancelar_viaje(request, idV):
    dateNow = timezone.now()
    viaje_cancelado = Viajes.objects.filter(id=idV).update(estado=3, fechor_cancelado=dateNow)

    return redirect('n_detalles_viaje', idV=idV)

def v_reservar_plaza(request, idV):
    dateNow = timezone.now()
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    viaje = Viajes.objects.get(id=idV)

    plaza_pendiente = Plazas(id_persona=usuario, id_viaje=viaje, flg_conductor=False, estado=1,
                             fechor_pendiente=dateNow)
    plaza_pendiente.save()

    return redirect('n_detalles_viaje', idV=idV)

def v_aceptar_pasajero(request, idV, idPl):
    dateNow = timezone.now()
    viaje = Viajes.objects.get(id=idV)
    if viaje.numero_asientos_libres > 0:
        viaje.numero_asientos_libres = F("numero_asientos_libres") - 1
        viaje.save()
        plaza_aceptada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado=2, fechor_confirmado=dateNow)
        messages.success(request, "¡¡¡Reserva registrada correctamente!!!")
        messages.success(request, "¡¡¡Ve preparando la maleta!!!")
    else:
        # se ha quedado sin plaza por reserva de otra de forma simultanea, por tanto se cancela ésta
        plaza_cancelada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado=4, fechor_cancelado=dateNow)
        messages.error(request, "¡¡¡Lo siento, se han agotado las plazas de este viaje en el último momento!!!")
        messages.error(request, "¡¡¡Se ha cancelado tu reserva automáticamente!!!")
        messages.error(request, "¡¡¡Prueba en otro viaje!!!")

    return redirect('n_detalles_viaje', idV=idV)

def v_rechazar_pasajero(request, idV, idPl):
    dateNow = timezone.now()
    plaza_rechazada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado=3, fechor_rechazado=dateNow)

    return redirect('n_detalles_viaje', idV=idV)

def v_cancelar_reserva(request, idV, idPl):
    dateNow = timezone.now()
    plaza_cancelada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado=4, fechor_cancelado=dateNow)

    return redirect('n_detalles_viaje', idV=idV)

def v_buscar_viaje(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    origen = request.POST.get('inputOrigen')
    destino = request.POST.get('inputDestino')
    fecha = request.POST.get('inputFecha')
    plazas = request.POST.get('inputPlazas')

    localizaciones = Localizaciones.objects.all()

    crit1 = Q(id_persona_receptor=OuterRef('id_persona_id'))
    Usuario_Viajes_Opiniones = Viajes.objects.values('id_persona_id', 'id_persona_id__nombre', 'ciudad_origen'
                                                        , 'ciudad_destino', 'fechor_ida'
                                                        , 'importe_total_asiento',
                                                        'numero_asientos_libres',
                                                        'estado', 'id_persona_id__pref_conversacion',
                                                        'id_persona_id__pref_fumar', 'id_persona_id__imagen') \
        .annotate(
            count_opiniones=Subquery(Opiniones.objects.filter(crit1).values('id_persona_receptor')
                                     .annotate(c=Count('*')).values('c')),
            avg_puntuacion=Subquery(Opiniones.objects.filter(crit1).values('id_persona_receptor')
                                    .annotate(avg=Avg('puntuacion')).values('avg'))
                ).filter(ciudad_origen=origen, ciudad_destino=destino, fechor_ida__date=fecha).order_by('fechor_ida')

    fV = UsuarioviajesopinionesFilter(request.POST, queryset=Usuario_Viajes_Opiniones)
    args = {
        'usuario': usuario,
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
            persona = form.save(commit=False)
            persona.id_usuario = request.user
            persona.save()
            messages.success(request, "¡¡¡Usuario creado correctamente!!!.")
            messages.success(request, f"¡¡¡ Bienvenid@ {request.user.email} !!!")
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

def v_nuevo_viaje(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None
    localizaciones = Localizaciones.objects.all()

    args = {
        "usuario": usuario,
        "localizaciones": localizaciones
    }

    if request.method == "POST":
        form = ViajesForm(request.POST)
        if form.is_valid():
            viaje = form.save(commit=False)
            viaje.id_persona = usuario
            viaje.numero_asientos_libres = viaje.numero_asientos_viaje
            viaje.importe_comision_asiento = viaje.importe_conductor_asiento/10
            viaje.importe_total_asiento = viaje.importe_comision_asiento + viaje.importe_conductor_asiento
            viaje.fechor_ida = datetime.combine(viaje.fecha_ida, viaje.hora_ida)
            viaje.save()
            #Insertamos la plaza del conductor
            plaza_conductor = Plazas(id_persona=usuario, id_viaje=viaje, flg_conductor=True, estado=2)
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

def v_menu_usuario(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None
    args = {
            "usuario": usuario
            }
    if request.method == "POST":
        form = PersonasForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            persona = form.save()
            persona.save()
            messages.success(request, "¡¡¡Datos de Usuario actualizados correctamente!!!")
            return redirect('n_menu_usuario')
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!!")
            return redirect('n_menu_usuario')
    else:
        # Se crea un form con la información del usuario logueado
        form = PersonasForm(instance=usuario)
        args.update({"form": form})
        return render(request, 'menu_usuario.html', args)

def v_menu_usuario_perfil(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None
    args = {
            "usuario": usuario
            }
    if request.method == "POST":
        form = PersonasForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            persona = form.save()
            persona.save()
            messages.success(request, "¡¡¡Datos de Usuario actualizados correctamente!!!")
            return redirect('n_menu_usuario_perfil')
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!!")
            return redirect('n_menu_usuario_perfil')
    else:
        # Se crea un form con la información del usuario logueado
        form = PersonasForm(instance=usuario)
        args.update({"form": form})
        return render(request, 'menu_usuario_perfil.html', args)

def v_menu_usuario_coches(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    try:
        vehiculos = Vehiculos.objects.all().filter(id_persona=usuario)
    except Vehiculos.DoesNotExist:
        vehiculos = None

    args = {
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
            return redirect('n_menu_usuario_coches')
        else:
            messages.error(request, "¡¡¡ERROR. El vehículo no se ha podido registrar!!!")
            return redirect('n_menu_usuario_coches')
    else:
        # Se crea un form con la información del usuario logueado
        form = VehiculosForm()
        args.update({"form": form})
        return render(request, 'menu_usuario_coches.html', args)

def v_menu_usuario_coches_eliminar(request, idVe):
    vehiculo=Vehiculos.objects.get(id=idVe)
    vehiculo.delete()

    return redirect('n_menu_usuario_coches')

def v_menu_usuario_coches_editar(request, idVe):
    vehiculo=Vehiculos.objects.get(id=idVe)
    args = {
        "vehiculo": vehiculo
    }
    if request.method == "POST":
        form = VehiculosForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            vehiculoform = form.save()
            vehiculoform.save()
            messages.success(request, "¡¡¡Datos de vehiculo actualizados correctamente!!!")
            return redirect('n_menu_usuario_coches')
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!! Prueba de nuevo!!!")
            return redirect('n_menu_usuario_coches')
    else:
        # Se crea un form con la información del usuario logueado
        form = VehiculosForm(instance=vehiculo)
        args.update({"form": form})
        return render(request, 'editar_coche.html', args)

def v_menu_usuario_preferencias(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    args = {
        "usuario": datos_usuario
    }
    if request.method == "POST":
        usuario.pref_conversacion = request.POST['pref_conversacion']
        usuario.pref_musica = request.POST['pref_musica']
        usuario.pref_mascota = request.POST['pref_mascota']
        usuario.pref_fumar = request.POST['pref_fumar']
        usuario.pref_comida = request.POST['pref_comida']
        usuario.save()
        messages.success(request, "¡¡¡Preferencias actualizadas correctamente!!!")
        return redirect('n_menu_usuario_preferencias')
    else:
        return render(request, 'menu_usuario_preferencias.html', args)

def v_menu_usuario_opiniones(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None
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
            "usuario": usuario,
            "opiniones_recibidas": opiniones_recibidas,
            "opiniones_publicadas": opiniones_publicadas,
            "avg_puntuacion": avg_puntuacion,
            "total_opiniones": total_opiniones,
            "opiniones_cat_dict": opiniones_cat_dict
    }
    return render(request, 'menu_usuario_opiniones.html', args)

def v_menu_usuario_notificaciones(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    args = {
        "usuario": usuario
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

        usuario.notif_noticiasofertas = notif_noticiasofertas
        usuario.notif_opiniones = notif_opiniones
        usuario.notif_reservas = notif_reservas
        usuario.save()
        messages.success(request, "¡¡¡Notificaciones actualizadas correctamente!!!")
        return redirect('n_menu_usuario_notificaciones')
    else:
        return render(request, 'menu_usuario_notificaciones.html', args)

def v_menu_usuario_pagoscobros(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    args = {
            "usuario": datos_usuario
            }

    return render(request, 'menu_usuario_pagoscobros.html', args)

def v_menu_usuario_contrasenya(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    args = {
        "usuario": usuario
    }
    if request.method == "POST":
        usuario.password = request.POST['nueva_password']
        usuario.save()
        messages.success(request, "¡¡¡Tu contraseña ha sido actualizada correctamente!!!")
        return redirect('n_menu_usuario_contrasenya')
    else:
        return render(request, 'menu_usuario_contrasenya.html', args)

def v_perfil_publico(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

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

def v_mis_viajes(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None


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
        "usuario": usuario,
        "filter": fV,
        "listado_plazas_viajes": listado_plazas_viajes
    }

    return render(request, 'mis_viajes.html', args)

def v_mis_mensajes(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

    #listado_conversaciones = Mensajes.objects.all().filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario)).values_list('id_persona_publicador','id_persona_receptor').distinct()
    #listado_conversaciones = Mensajes.objects.all().filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario))

    listado_conversaciones = Mensajes.objects.values('id_persona_publicador__nombre', 'id_persona_publicador__apellido1', 'id_persona_publicador__id', 'id_persona_publicador__imagen'
                                                        , 'id_persona_receptor__nombre', 'id_persona_receptor__apellido1', 'id_persona_receptor__id', 'id_persona_receptor__imagen'
                                                        )\
        .annotate(max_fec_created=Max('fec_created'))\
        .filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario))
    print(listado_conversaciones.count())
    fM = MensajesFilter(request.GET, queryset=listado_conversaciones)

    args = {
            "usuario": usuario,
            "filter": fM
            }

    return render(request, "mis_mensajes.html", args)


def v_conversacion(request, idPc):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None
    usuario_receptor = Personas.objects.get(id=idPc)
    listado_mensajes = Mensajes.objects.filter(Q(id_persona_publicador=usuario, id_persona_receptor=usuario_receptor) | Q(id_persona_publicador=usuario_receptor, id_persona_receptor=usuario)).order_by('fec_created')
    args = {
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

def v_opiniones_recibidas_main(request):
    if request.user.is_authenticated:
        usuario = Personas.objects.get(id_usuario=request.user.id)
    else:
        usuario = None

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
        "usuario": usuario,
        "avg_puntuacion": avg_puntuacion,
        "total_opiniones": total_opiniones,
        "opiniones_recibidas": opiniones_recibidas,
        "opiniones_cat_dict": opiniones_cat_dict
    }

    return render(request, 'opiniones_recibidas_main.html', args)


