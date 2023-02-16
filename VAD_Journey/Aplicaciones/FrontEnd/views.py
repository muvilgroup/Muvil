from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, date
from .forms import PersonasForm, ViajesForm, VehiculosForm
from django.contrib import messages

from .models import Personas, Viajes, Vehiculos

# Create your views here.
def v_pagina_principal(request):
    dateNow = datetime.date(datetime.now())
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

    # Se recuperan los 4 próximos viajes
    ##viajesProximos = Viajes.objects.all().order_by('-fecha_ida', '-hora_ida').filter(fecha_ida__gte=dateNow,hora_ida__gte=timeNow)[0:3]
    viajesProximos = Viajes.objects.all().filter(fecha_ida__gte=dateNow).order_by('fecha_ida')[0:4]

    args = {
        'idP': idP,
        'usuario': datos_usuario,
        'viajesProximos':viajesProximos,
        'numAlert': numalert
    }
    return render(request, "pagina_principal.html", args)

def v_buscar_viaje(request, idP):
    origen = request.POST.get('inputOrigen')
    destino = request.POST.get('inputDestino')
    fecha = request.POST.get('inputFecha')
    plazas = request.POST.get('inputPlazas')
    #print(plazas)

    viajesListados = Viajes.objects.filter(ciudad_origen=origen, ciudad_destino=destino, fecha_ida=fecha).order_by('fecha_ida')

    args = {
        'idP': idP,
        'viajes': viajesListados,
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
    if request.method == "POST":
        form = ViajesForm(request.POST)
        if form.is_valid():
            viaje = form.save(commit=False)
            viaje.id_persona = Personas.objects.get(id=idP)
            viaje.importe_comision_asiento = viaje.importe_conductor_asiento/10
            viaje.importe_total_asiento = viaje.importe_comision_asiento + viaje.importe_conductor_asiento
            viaje.fechor_ida = datetime.combine(viaje.fecha_ida, viaje.hora_ida)
            viaje.save()
            messages.success(request, "¡¡¡Viaje publicado correctamente!!!.")
            return redirect('n_pagina_principal')
        else:
            messages.error(request, "¡¡¡ERROR. Viaje no publicado!!!.")
            return redirect('n_pagina_principal')
    else:
        form = ViajesForm()
        return render(request, 'nuevo_viaje.html', {'form': form})

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
    datos_usuario = Personas.objects.get(id=idP)

    args = {
            "idP": idP,
            "usuario": datos_usuario
            }

    return render(request, 'menu_usuario_coches.html', args)

def v_menu_usuario_preferencias(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
            "idP": idP,
            "usuario": datos_usuario
            }

    return render(request, 'menu_usuario_preferencias.html', args)

def v_menu_usuario_opiniones(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
            "idP": idP,
            "usuario": datos_usuario
            }

    return render(request, 'menu_usuario_opiniones.html', args)

def v_menu_usuario_notificaciones(request, idP):
    datos_usuario = Personas.objects.get(id=idP)

    args = {
            "idP": idP,
            "usuario": datos_usuario
            }

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

    return render(request, 'menu_usuario_contrasenya.html', args)

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