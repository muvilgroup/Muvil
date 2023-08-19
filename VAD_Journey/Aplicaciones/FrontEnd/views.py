from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, date
from .forms import PersonasForm, ViajesForm, VehiculosForm, ContactoForm, CambiarPassForm, ResetearPassForm,\
    RegistrarUsuarioForm, ImportExportForm
from django.contrib import messages
from django.db.models import Sum, Count, Avg, CharField, Value, F, Q, Max, Subquery, OuterRef
from .choices import categorias_puntuacion, estados_viajes
from .templatetags.filters import ViajesFilter, MensajesFilter, UsuarioviajesopinionesFilter
from django.views.generic import View
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.mail import send_mail
from .token import token_activacion_usuario
from .models import Personas, Viajes, Vehiculos, Opiniones, Plazas, Mensajes, Localizaciones
from ..users.admin import UserCreationForm as CustomUserCreationForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import EmailMessage
from .decorators import check_logued_usuario, get_persona_usuario, get_vehiculos_usuario
from tablib import Dataset
from .resources import LocalizacionesResource
from allauth.socialaccount.models import SocialAccount
from PIL import Image
import requests
import io
import pytz



# Create your views here.
class Vregistrousuario (View):
    def get(self, request):
        form = RegistrarUsuarioForm()
        datos = {
            'form': form,
        }
        return render(request,"registro_usuario.html", datos)

    def post(self, request):
        form = RegistrarUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = False
            usuario.save()
            activacionEmail(request, usuario, form.cleaned_data.get('email'))
            return redirect('n_pagina_principal')
        else:
            password1 = form.data['password1']
            password2 = form.data['password2']
            email = form.data['email']
            #print(form.errors)
            #print('------------')
            #print(form.errors.as_data())
            for msg in form.errors.as_data():
                if msg == 'email':
                    messages.error(request, f"La direccion de email {email} no es válida o ya existe")
                if msg == 'password2' and password1 == password2:
                    messages.error(request, f"La contraseña {password1} no es lo suficientemente robusta")
                elif msg == 'password2' and password1 != password2:
                    messages.error(request,
                                   f"Los 2 campos de contraseña no coinciden")
            datos = {
                'form': form,
            }
            return render(request,'registro_usuario.html', datos)

def v_activar(request, uidb64, token):
    Usuario = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except:
        user = None

    if usuario is not None and token_activacion_usuario.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        login(request, usuario, backend='Aplicaciones.users.backends.CustomEmailAuthBackend')
        messages.success(request, "<h2>Gracias por la confirmación por email!</h2><hr> <p>Tu cuenta ha sido activada, "
                                  "completa los datos de tu usuario y empieza a viajar!</p>")
        return redirect('n_nuevo_usuario')
    else:
        messages.error(request, "El enlace de activación no es válido!")

    return redirect('n_pagina_principal')

def activacionEmail(request, usuario, to_email):
    asunto = "Activa tu cuenta de usuario"
    mensaje = render_to_string ("mail_activacion_usuario.html", {
        'user': usuario.email,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(usuario.pk)),
        'token': token_activacion_usuario.make_token(usuario),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(asunto, mensaje, to=[to_email])
    if email.send():
        messages.success(request, f"<h2>Ya falta muy poco!!!</h2><hr> \
        <p>Por favor, diríjase a la bandeja de entrada o spam de su correo \
        electrónico {usuario} y active su cuenta pulsando sobre el link de registro enviado.</p>")
    else:
        messages.error(request, f'Ha ocurrido un error al enviar el mail de confirmación a {to_email}, \
        por favor, comprueba si está bien escrita la dirección de correo.')

def v_resetear_contrasenya(request):
    if request.method == 'POST':
        form = ResetearPassForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("mail_resetear_contrasenya.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': token_activacion_usuario.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Reseteo de contraseña enviado</h2><hr>
                        <p>
                            Le hemos enviado instrucciones por correo electrónico para resetear su contraseña, si existe una cuenta con el correo electrónico que ingresó,
                            debería recibirlo en breve.<br>Si no recibe un correo electrónico, asegúrese de haber ingresado la dirección
                            con la que te registraste y revisa tu carpeta de correo no deseado (spam).
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Ha ocurrido un problema al enviar el mail de reseteo de contraseña! <b>SERVER PROBLEM</b>")

            return redirect('n_pagina_principal')

        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, "Debes superar el test reCaptcha")
                continue

    form = ResetearPassForm()
    return render(
        request=request,
        template_name="resetear_contrasenya.html",
        context={"form": form}
        )

def v_confirmacion_reset(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and token_activacion_usuario.check_token(user, token):
        if request.method == 'POST':
            form = CambiarPassForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Su contraseña se ha cambiado. Ya puede <b>iniciar sesión</b> de nuevo.")
                return redirect('n_pagina_principal')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = CambiarPassForm(user)
        return render(request, 'cambiar_contrasenya.html', {'form': form})
    else:
        messages.error(request, "El link de reseteo ha caducado!")

    messages.error(request, 'Algo ha ido mal, redirigiendo a la página principal!')
    return redirect('n_pagina_principal')

def v_signup_redirect(request):
    messages.error(request, "<h2 class='text-center'>Algo ha ido mal!!! Quizás ya exista una cuenta con ese email!!!</h2>")
    return redirect("n_pagina_principal")

def v_import_export(request):
    dateNow = timezone.now()
    if request.method == 'POST':
        form = ImportExportForm(request.POST, request.FILES)
        if form.is_valid():
            #localizaciones = LocalizacionesResource()
            dataset = Dataset()
            new_localizaciones = request.FILES['fichero_import']
            modelo = request.POST.get('modelo', False)
            imported_data = dataset.load(new_localizaciones.read(), format='xlsx')

            for data in imported_data:
                value = Localizaciones(
                    id=data[0],
                    id_comunidadauto=data[1],
                    comunidadauto=data[2],
                    id_provincia=data[3],
                    provincia=data[4],
                    id_isla=data[5],
                    isla=data[6],
                    dc=data[7],
                    id_municipio=data[8],
                    municipio=data[9],
                    direccion=data[10],
                    coordenada_x=None,
                    coordenada_y=None,
                    fec_created=dateNow,
                    fec_updated=dateNow
                )
                value.save()

            messages.success(request,f"<h2 class='text-center'>¡¡¡El fichero se ha cargado en el modelo <strong>{modelo}</strong> correctamente!!!</h2>")
        else:
            messages.error(request, "¡¡¡Error en el formulario!!!")
            messages.error(request, form.errors)

    form = ImportExportForm()

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
    datos = {
        'form': form,
    }
    return render(request, 'import_export.html', datos)

def v_pagina_principal(request):
    dateNow = timezone.now()

    if request.session.get('first_time', 0) == 0:
        first_time = request.session['first_time'] = 1
    else:
        first_time = request.session['first_time'] = 2

    # Se comprueba si se ha introducido el user/pass
    email_input = request.POST.get('txtEmail', False)
    pass_input = request.POST.get('txtPass', False)

    if email_input and pass_input and not request.user.is_authenticated:
        user = authenticate(username=email_input, password=pass_input)
        if user is not None:
            login(request, user, backend='Aplicaciones.users.backends.CustomEmailAuthBackend')
        else:
            messages.error(request, "¡¡¡Usuario o Contraseña incorrectos!!! Vuelve a intentarlo!!!")

    if request.user.is_authenticated:
        user_auth = request.user
        try:
            usuario = Personas.objects.get(id_usuario=user_auth.id)
        except Personas.DoesNotExist:
            # Aqui entra cuando volvemos del login por FB pero no hay persona creada y se crea con los datos de FB
            extra_data = SocialAccount.objects.get(user=user_auth).extra_data
            nombre = extra_data.get('given_name')
            apellido1 = extra_data.get('family_name')
            imagen_url = extra_data.get('picture')
            usuario = Personas(id_usuario=user_auth, nombre=nombre, apellido1=apellido1)
            usuario.save()
            login(request, user_auth, backend='Aplicaciones.users.backends.CustomEmailAuthBackend')
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
        'numAlert': numalert,
        'first_time': first_time,
    }
    return render(request, "pagina_principal.html", args)

@check_logued_usuario
@get_persona_usuario
def v_detalles_viaje(request, idV, usuario):

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
        'idP': idP,
        'viaje': viaje,
        'plazas': plazas,
        'flg_reserva_pend_conf': flg_reserva_pend_conf,
        'usuario_conductor': usuario_conductor,
        'opiniones_escritas_x_cond': opiniones_escritas_x_cond,
        'opinion_escrita_a_cond': opinion_escrita_a_cond,
    }

    return render(request, "detalles_viaje.html", args)

@check_logued_usuario
def v_cancelar_viaje(request, idV):
    dateNow = timezone.now()
    viaje_cancelado = Viajes.objects.filter(id=idV).update(estado=3, fechor_cancelado=dateNow)

    return redirect('n_detalles_viaje', idV=idV)

@check_logued_usuario
@get_persona_usuario
def v_reservar_plaza(request, idV, usuario):
    dateNow = timezone.now()

    viaje = Viajes.objects.get(id=idV)

    plaza_pendiente = Plazas(id_persona=usuario, id_viaje=viaje, flg_conductor=False, estado=1,
                             fechor_pendiente=dateNow)
    plaza_pendiente.save()

    return redirect('n_detalles_viaje', idV=idV)

@check_logued_usuario
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

@check_logued_usuario
def v_rechazar_pasajero(request, idV, idPl):
    dateNow = timezone.now()
    plaza_rechazada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado=3, fechor_rechazado=dateNow)

    return redirect('n_detalles_viaje', idV=idV)

@check_logued_usuario
def v_cancelar_reserva(request, idV, idPl):
    dateNow = timezone.now()
    plaza_cancelada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado=4, fechor_cancelado=dateNow)

    return redirect('n_detalles_viaje', idV=idV)

# no validamos aqui el logueo del usuario ya que puede acceder sin él
def v_buscar_viaje(request):

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
        'localizaciones': localizaciones,
        'filter': fV,
        'ciudad_origen': origen,
        'ciudad_destino': destino,
        'fecha_viaje': fecha,
        'nro_plazas': plazas
    }

    return render(request, "buscar_viaje.html", args)

@check_logued_usuario
def v_nuevo_usuario(request):
    if request.method == "POST":
        form = PersonasForm(request.POST, request.FILES)
        if form.is_valid():
            persona = form.save(commit=False)
            # INICIO validacion +18 años
            if datetime.now().year - persona.fec_nacimiento.year < 18:
                messages.error(request, "¡¡¡Error, debes tener +18 años!!!")
                return redirect('n_nuevo_usuario')
            # FIN validacion +18 años
            persona.id_usuario = request.user
            persona.save()
            messages.success(request, "¡¡¡Usuario creado correctamente!!!.")
            messages.success(request, f"¡¡¡ Bienvenid@ {request.user.email} !!!")
            return redirect('n_pagina_principal')
        else:
            messages.error(request, "¡¡¡ERROR. Usuario no creado!!!.")
            for field in form:
                if field.errors:
                    messages.error(request, f"{field.label}: {field.errors}")
            return redirect('n_nuevo_usuario')
    else:
        form = PersonasForm()
        return render(request, 'nuevo_usuario.html', {'form': form})

def v_listado_usuarios(request):
    usuariosListados = Personas.objects.all()

    args = {"usuarios": usuariosListados}

    return render(request, "listado_usuarios.html", args)

@check_logued_usuario
@get_persona_usuario
@get_vehiculos_usuario
def v_nuevo_viaje(request, usuario, vehiculos):
    if not vehiculos:
        messages.error(request, "¡¡¡Por favor, registra 1 vehiculo antes de publicar viajes!!!.")
        return redirect('n_menu_usuario_coches')

    localizaciones = Localizaciones.objects.all()

    args = {
        "usuario": usuario,
        "localizaciones": localizaciones
    }

    if request.method == "POST":
        form = ViajesForm(request.POST, user=request.user)
        if form.is_valid():
            viaje = form.save(commit=False)
            v_fechor_ida = datetime.combine(viaje.fecha_ida, viaje.hora_ida)
            # INICIO Validacion de viajes a pasado
            if v_fechor_ida < datetime.now():
                messages.error(request, "¡¡¡No se pueden publicar viajes a pasado!!!")
                return redirect('n_nuevo_viaje')
            # FIN Validacion de viajes a pasado
            # INICIO Validacion de plazas maximas superadas
            vehiculo_obj = Vehiculos.objects.get(id=viaje.id_vehiculo.id)
            if viaje.numero_asientos_viaje > getattr(vehiculo_obj, 'numero_asientos'):
                messages.error(request, "¡¡¡No se pueden ofertar mas plazas de las que el vehiculo acepta!!! Prueba otra vez.")
                return redirect('n_nuevo_viaje')
            # FIN Validacion de plazas maximas superadas
            # INICIO Validacion de plazas mayor que 0
            if viaje.numero_asientos_viaje <= 0:
                messages.error(request, "¡¡¡No se pueden publicar viajes sin plazas libres!!!")
                return redirect('n_nuevo_viaje')
            # FIN Validacion de plazas mayor que 0
            viaje.id_persona = usuario
            viaje.numero_asientos_libres = viaje.numero_asientos_viaje
            viaje.importe_comision_asiento = viaje.importe_conductor_asiento/10
            viaje.importe_total_asiento = viaje.importe_comision_asiento + viaje.importe_conductor_asiento
            viaje.fechor_ida = v_fechor_ida
            viaje.id_vehiculo = viaje.id_vehiculo
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
        form = ViajesForm(user=request.user)
        args.update({'form': form})
        return render(request, 'nuevo_viaje.html', args)

def v_listado_viajes(request):
    viajesListados = Viajes.objects.all()

    args = {"viajes": viajesListados}

    return render(request, "listado_viajes.html", args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario(request, usuario):
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

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_perfil(request, usuario):
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

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_coches(request, usuario):
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
            if vehiculo.anyo_antiguedad > datetime.now().year:
                messages.error(request, "¡¡¡El año de antigüedad no puede ser posterior al actual!!!")
                return redirect('n_menu_usuario_coches')
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

@check_logued_usuario
def v_menu_usuario_coches_eliminar(request, idVe):
    vehiculo=Vehiculos.objects.get(id=idVe)
    # INICIO validacion coche con viajes pendientes
    viajes_pend_count = Viajes.objects.all().filter(Q(id_vehiculo=vehiculo, estado=1)).count()
    if viajes_pend_count > 0:
        messages.error(request, f"¡¡¡Error, <strong>este vehiculo tiene viajes {viajes_pend_count} pendientes</strong> y no se puede "
                                f"eliminar hasta que no se completen esos viajes!!!")
        return redirect('n_menu_usuario_coches')
    # FIN validacion coche con viajes pendientes

    vehiculo.delete()

    return redirect('n_menu_usuario_coches')

@check_logued_usuario
def v_menu_usuario_coches_editar(request, idVe):
    vehiculo=Vehiculos.objects.get(id=idVe)
    args = {
        "vehiculo": vehiculo
    }
    if request.method == "POST":
        form = VehiculosForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            vehiculoform = form.save(commit=False)
            if vehiculo.anyo_antiguedad > datetime.now().year:
                messages.error(request, "¡¡¡El año de antigüedad no puede ser posterior al actual!!!")
                return redirect('n_menu_usuario_coches')
            print(vehiculoform.imagen_vehiculo)
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

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_preferencias(request, usuario):
    args = {
        "usuario": usuario
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

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_opiniones(request, usuario):
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

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_notificaciones(request, usuario):

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

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_pagoscobros(request, usuario):

    args = {
            "usuario": usuario
            }

    return render(request, 'menu_usuario_pagoscobros.html', args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_contrasenya(request, usuario):
    user = request.user
    if request.method == 'POST':
        form = CambiarPassForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu contraseña ha sido modificada!!!")
            login(request, user, backend='Aplicaciones.users.backends.CustomEmailAuthBackend')
            return redirect('n_pagina_principal')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = CambiarPassForm(user)

    args ={
        'usuario': usuario,
        'form': form
    }
    return render(request, 'menu_usuario_contrasenya.html', args)

@check_logued_usuario
@get_persona_usuario
def v_perfil_publico(request, usuario):

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

@check_logued_usuario
@get_persona_usuario
def v_mis_viajes(request, usuario):

    idP = usuario.id

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
        "idP": idP,
        "filter": fV,
        "listado_plazas_viajes": listado_plazas_viajes
    }

    return render(request, 'mis_viajes.html', args)

@check_logued_usuario
@get_persona_usuario
def v_mis_mensajes(request, usuario):

    idP = usuario.id

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
            "idP": idP,
            "filter": fM
            }

    return render(request, "mis_mensajes.html", args)

@check_logued_usuario
@get_persona_usuario
def v_conversacion(request, idPc, usuario):

    idP = usuario.id

    usuario_receptor = Personas.objects.get(id=idPc)
    listado_mensajes = Mensajes.objects.filter(Q(id_persona_publicador=usuario, id_persona_receptor=usuario_receptor) | Q(id_persona_publicador=usuario_receptor, id_persona_receptor=usuario)).order_by('fec_created')

    args = {
            "usuario": usuario,
            "idP": idP,
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

@check_logued_usuario
@get_persona_usuario
def v_opiniones_recibidas_main(request, usuario):

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

@check_logued_usuario
@get_persona_usuario
def v_contacto(request, usuario):

    if request.method == "POST":
        email = request.POST.get("email2")
        asunto = "Contacto: " + request.POST.get("subject")
        mensaje = f"Mensaje de {email}: \n\n" + request.POST.get("message")
        try:
            send_mail(asunto,
                      mensaje,
                      email,
                      ["vad.journey@gmail.com"])
            return redirect("/contacto/?valido")
        except:
            return redirect("/contacto/?error")

    datos = {

    }
    return render(request, "contacto.html", datos)

