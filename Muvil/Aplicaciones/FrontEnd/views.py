# Pasarela de Pago
import time
#import swagger_client
#from swagger_client.rest import ApiException
from pprint import pprint

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import PersonasForm, ViajesForm, VehiculosForm, ContactoForm, CambiarPassForm, ResetearPassForm,\
    RegistrarUsuarioForm, ImportExportForm, LoginnForm, VueltaViajesForm, CaparazonesForm
from .utils import codificar_numeros
from .geolocalizacion import Geolocalizacion
from django.contrib import messages
from django.db.models import Sum, Count, Avg, CharField, Value, F, Q, Max, Subquery, OuterRef, Func
from .choices import categorias_puntuacion, estados_viajes
from .templatetags.filters import MisViajesFilter, BuscarViajeFilter, MensajesFilter, UsuarioviajesopinionesFilter
from django.views.generic import View
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.mail import send_mail
from .validaciones import ValidacionesViajes
from .alertas_pagina_principal import AlertasPrincipal
from .token import token_activacion_usuario
from .models import Personas, Viajes, Vehiculos, Opiniones, Plazas, Mensajes, Localizaciones, Caparazones
from allauth.socialaccount.models import SocialAccount
from ..users.admin import UserCreationForm as CustomUserCreationForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import EmailMessage, EmailMultiAlternatives
from .decorators import check_logued_usuario, get_persona_usuario, get_vehiculos_usuario
from tablib import Dataset
from .resources import LocalizacionesResource
from PIL import Image
import requests
import io
import pytz
#import pywhatkit
from django.http import JsonResponse
from geopy.geocoders import Nominatim



# Create your views here.
class Vregistrousuario (View):
    def get(self, request):
        form = RegistrarUsuarioForm()
        datos = {
            'form': form,
        }
        return render(request, "registro_usuario.html", datos)

    def post(self, request):
        form = RegistrarUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = False
            usuario.save()
            activacionEmail(request, usuario, form.cleaned_data.get('email'))
            return render(request, 'pagina_principal.html', {})
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
            return render(request, 'registro_usuario.html', datos)

def v_activar(request, uidb64, token):
    Usuario = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except:
        usuario = None

    if usuario is not None and token_activacion_usuario.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        login(request, usuario, backend='Aplicaciones.users.backends.CustomEmailAuthBackend')
        messages.success(request, "<h2>Gracias por la confirmación por email!</h2><hr> <p>Tu cuenta ha sido activada, "
                                  "completa los datos de tu usuario y empieza a viajar!</p>")
        return redirect('n_nuevo_usuario')
    elif usuario is not None and not token_activacion_usuario.check_token(usuario, token):
        # El enlace ha caducado y se debe eliminar el usuario para que pueda volver a registrarlo.
        usuario.delete()
        messages.error(request, "¡El enlace de activación ha caducado! \
                                <p>¡Debes repetir el proceso de alta de usuario!</p>")
    else:
        messages.error(request, "¡El enlace de activación no es válido! \
                                <p>¡Debes repetir el proceso de alta de usuario!</p>")

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
        electrónico {usuario} y active su cuenta pulsando sobre el link de registro enviado.</p> \
        <p> Es importante que lo active antes de {int(settings.PASSWORD_RESET_TIMEOUT/3600)} horas, de lo contrario \
                                  deberá volver a repetir el proceso.")
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

def v_pasarela_pago(request):
    if request.method == "POST":
        #print(request.POST.get('paytpvToken', False))

        # create an instance of the API class
        api_instance = swagger_client.BalanceApi()
        api_instance2 = swagger_client.CardsApi()
        api_instance3 = swagger_client.PaymentsApi()
        body = {
                "terminal": 65660
                }
        body2 = {
            "terminal": "65660",
            "jetToken": request.POST.get('paytpvToken', False)
        }
        pAYCOMETAPITOKEN = "892c972dc58b350c814e7c2388d14d4b32a10967"

        try:
            api_response = api_instance2.add_user(body=body2, paycomet_api_token=pAYCOMETAPITOKEN)
            dict_api_response = api_response.to_dict()
            #pprint(api_response)
            id_user = dict_api_response["id_user"]
            token_user = dict_api_response["token_user"]
            body3 = {
                    "payment": {
                                "terminal": "65660",
                                "amount": "77",
                                "currency": "EUR",
                                "idUser": id_user,
                                "tokenUser": token_user,
                                "methodId": "1",
                                "order": "MUVIL12345000",
                                "originalIp": "127.0.0.1",
                                "secure": "1",
                                "urlOk": "https://www.paycomet.com/url-ok",
                                "urlKo": "https://www.paycomet.com/url-ko"
                                }
                    }
            api_response = api_instance3.execute_purchase(body=body3, paycomet_api_token=pAYCOMETAPITOKEN)
            #pprint(api_response)
        except ApiException as e:
            print("Exception when calling CardsApi->addUser: %s\n" % e)

        return render(request, 'pasarela_pago.html', {})
    else:
        return render(request, 'pasarela_pago.html', {})

'''
def v_enviar_whatsapp(request):
    pywhatkit.sendwhatmsg('+34650125557', 'Prueba desde Muvil', 18, 43)
'''

def v_pagina_principal(request):
    dateNow = timezone.now()

    if request.session.get('first_time', 0) == 0:
        first_time = request.session['first_time'] = 1
    else:
        first_time = request.session['first_time'] = 2

    if request.method == "POST":
        # Se recuperan los introducidos user/pass
        email_input = request.POST.get('txtEmail', False)
        pass_input = request.POST.get('txtPass', False)

        if not request.user.is_authenticated:
            user = authenticate(username=email_input, password=pass_input)
            if user is not None:
                alertas = AlertasPrincipal(usuario_input=user)
                lista_alertas = alertas.alert_mensajes_salida()
                login(request, user, backend='Aplicaciones.users.backends.CustomEmailAuthBackend')
                if not lista_alertas:
                    messages.success(request, f"¡Bienvenid@ {request.user.email}!")
                else:
                    for mensaje in lista_alertas:
                        messages.success(request, mensaje)

                # con este código volvemos a la última pagina en la que estabamos antes del login
                next = request.POST.get('next', '/')
                return HttpResponseRedirect(next)
            else:
                messages.error(request, "¡¡¡Usuario o Contraseña incorrectos!!! Vuelve a intentarlo!!!<br>\
                      Si has olvidado tu contraseña puedes resetearla aquí <a class='btn btn-warning fw-bold boton-3d' href='resetear_contrasenya/'>Cambiar Contraseña</a>")


    if request.user.is_authenticated:
        user = request.user
        alertas = AlertasPrincipal(usuario_input=user)
        lista_alertas = alertas.alert_mensajes_salida()
        if lista_alertas:
            for mensaje in lista_alertas:
                messages.success(request, mensaje)
        try:
            usuario = Personas.objects.get(id_usuario=user.id)
        except Personas.DoesNotExist:
            # Aqui entra cuando volvemos del login por Google pero no hay persona creada aún
            extra_data = SocialAccount.objects.get(user=user).extra_data
            initial_values = {
                "nombre": extra_data.get('given_name'),
                "apellido1": extra_data.get('family_name'),
                "imagen": extra_data.get('picture')
            }
            request.session['google_initial_values'] = initial_values
            return redirect('n_nuevo_usuario')

    else:
        usuario = None


    numalert = 1
    localizaciones = Localizaciones.objects.all()

    # Se recuperan los 4 próximos viajes
    ##viajesProximos = Viajes.objects.order_by('-fecha_ida', '-hora_ida').filter(fecha_ida__gte=dateNow,hora_ida__gte=timeNow)[0:3]
    #viajesProximos = Viajes.objects.filter(fechor_ida__gte=dateNow).order_by('fechor_ida')[0:4]
    crit1 = Q(id_persona_receptor=OuterRef('id_persona_id'))
    viajesProximos = Viajes.objects.values('id_persona_id', 'id_persona_id__nombre', 'ciudad_origen'
                                                     ,'id', 'ciudad_destino', 'fechor_ida'
                                                     ,'importe_total_asiento','fechor_llegada'
                                                     ,'numero_asientos_libres', 'flg_confirmacion_auto',
                                                     'estado', 'id_persona_id__pref_conversacion',
                                                     'id_persona_id__pref_fumar', 'id_persona_id__imagen',
                                                    'distancia_kms','duracion_min') \
        .annotate(count_opiniones=Subquery(Opiniones.objects.filter(crit1).
                                           values('id_persona_receptor').annotate(c=Count('*')).values('c')),
                  avg_puntuacion=Subquery(Opiniones.objects.filter(crit1).
                                           values('id_persona_receptor').annotate(avg=Avg('puntuacion')).values('avg'))) \
        .filter(Q(fechor_ida__gte=dateNow, numero_asientos_libres__gt=0, estado=1)) \
        .order_by('fechor_ida')[0:4]
    args = {
        'usuario': usuario,
        'localizaciones': localizaciones,
        'viajesProximos': viajesProximos,
        'numAlert': numalert,
        'first_time': first_time,
    }

    return render(request, "pagina_principal.html", args)

@get_persona_usuario
def v_detalles_viaje(request, idV, persona):

    if persona:
        idP = persona.id
    else:
        idP = None
        messages.error(request, "Hola :) ¡Debes iniciar sesión para reservar plaza en este viaje!")

    viaje = Viajes.objects.get(id=idV)
    plazas = Plazas.objects.filter(Q(id_viaje=idV, flg_conductor=False, estado__in=(1, 2))) # plazas pendientes o confirmadas
    flg_reserva_pend_conf = plazas.filter(Q(id_persona=idP)).exists()
    flg_reserva_confirmada = plazas.filter(Q(id_persona=idP, estado=2)).exists()

    if flg_reserva_confirmada and viaje.estado == 1:
        messages.success(request, "¡¡¡Enhorabuena, tu plaza ha sido confirmada!!!\
                                    <p>Ahora puedes ver el <strong>número de contacto del conductor</strong> para \
                                     cerrar los detalles del viaje</p>")

    if viaje.id_persona == persona:
        usuario_conductor = True
    else:
        usuario_conductor = False

    if usuario_conductor:
        opiniones_escritas_x_cond = Opiniones.objects.filter(Q(id_viaje=idV, id_persona_publicador=idP))
        opinion_escrita_a_cond = None
        # Estos 2 flags son para saber si el conductor o pasajero ha confirmado el viaje como finalizado o problematico
        flg_viaje_fin_prob_cond = Plazas.objects.filter(Q(id_viaje=idV, flg_conductor=True, estado_plaza_viaje__in=(3, 4))).exists()
        flg_viaje_fin_prob = None
    else:
        opiniones_escritas_x_cond = None
        opinion_escrita_a_cond = Opiniones.objects.filter(Q(id_viaje=idV, id_persona_publicador=idP, id_persona_receptor=viaje.id_persona.id))
        # Estos 2 flags son para saber si el conductor o pasajero ha confirmado el viaje como finalizado o problematico
        flg_viaje_fin_prob_cond = None
        flg_viaje_fin_prob = Plazas.objects.filter(Q(id_viaje=idV, flg_conductor=False, id_persona=idP, estado_plaza_viaje__in=(3, 4))).exists()

    args = {
        'usuario': persona,
        'idP': idP,
        'viaje': viaje,
        'plazas': plazas,
        'flg_reserva_pend_conf': flg_reserva_pend_conf,
        'flg_reserva_confirmada': flg_reserva_confirmada,
        'flg_viaje_fin_prob': flg_viaje_fin_prob,
        'usuario_conductor': usuario_conductor,
        'opiniones_escritas_x_cond': opiniones_escritas_x_cond,
        'opinion_escrita_a_cond': opinion_escrita_a_cond,
        'flg_viaje_fin_prob_cond': flg_viaje_fin_prob_cond
    }

    return render(request, "detalles_viaje.html", args)

@check_logued_usuario
def v_cancelar_viaje(request, idV):
    dateNow = timezone.now()
    viaje_cancelado = Viajes.objects.filter(id=idV)
    viaje_cancelado.update(estado=3, fechor_cancelado=dateNow)
    # Se cancelan las plazas del viaje
    plazas_canceladas = Plazas.objects.filter(id_viaje=idV)
    plazas_canceladas.update(estado=4, fechor_cancelado=dateNow)

    # Extraer de QerySet el valor de un campo
    fechor_ida = (viaje_cancelado.values_list('fechor_ida', flat=True)[0]).date()
    ciudad_origen = viaje_cancelado.values_list('ciudad_origen', flat=True)[0]
    ciudad_destino = viaje_cancelado.values_list('ciudad_destino', flat=True)[0]
    to_email_plazas_list = list(plazas_canceladas.values_list('id_persona__id_usuario__email', flat=True))
    mail_asunto = "VIAJE CANCELADO!!!"
    mail_mensaje = (f""
               f"¡Lo sentimos!\n"
               f"El conductor ha cancelado tu viaje que salía el día {fechor_ida} de {ciudad_origen} hasta {ciudad_destino}.\n"
               f"Entra en tu portal y busca otro viaje similar.\n\nLa esperanza es lo último que se pierde :)"
               )
    alerta_mensaje = f"VIAJE CANCELADO! Hemos notificado a los pasajeros que estuvieran confirmados en el viaje."
    if len(to_email_plazas_list) > 0:
        enviarEmail_alertas(request, request.user, to_email_plazas_list, mail_asunto, mail_mensaje, alerta_mensaje)

    return redirect('n_detalles_viaje', idV=idV)

def enviarEmail_alertas(request, user, to_email, asunto, mensaje, alerta):
    """
    to_email: debe ser una list para que se envíe a varios destinatarios
    """
    asunto = asunto
    mensaje = render_to_string ("mail_template_alertas.html", {
        'user': user.email,
        'mensaje': mensaje,
    })
    email = EmailMessage(asunto, mensaje, to=to_email)
    if email.send():
        #print(nadaaaa)
        if alerta:
            messages.success(request, alerta)
    else:
        messages.error(request, f'El envío de mail ha fallado!')

@check_logued_usuario
@get_persona_usuario
def v_reservar_plaza(request, idV, persona):
    dateNow = timezone.now()
    viaje = Viajes.objects.get(id=idV)

    # Devolver plazas en viajes pendientes o confirmados que esten en el mismo slot de tiempo
    criterio_plazas_pend = Q(id_persona_id=persona.id, estado=1, id_viaje__fechor_ida__range=(viaje.fechor_ida, viaje.fechor_llegada)) \
               | Q(id_persona=persona, estado=1, id_viaje__fechor_llegada__range=(viaje.fechor_ida, viaje.fechor_llegada))
    criterio_plazas_conf = Q(id_persona_id=persona.id, estado=2, id_viaje__fechor_ida__range=(viaje.fechor_ida, viaje.fechor_llegada)) \
                           | Q(id_persona_id=persona.id, estado=2, id_viaje__fechor_llegada__range=(viaje.fechor_ida, viaje.fechor_llegada))
    plazas_coincidentes = Plazas.objects.filter(criterio_plazas_pend | criterio_plazas_conf)

    if plazas_coincidentes:
        messages.error(request, "¡¡¡ERROR!!! Ya tienes una plaza confirmada o pendiente en otro viaje en esta franja \
                                        horaria, no puedes hacer 2 viajes al mismo tiempo... al menos físicamente :)")
        return redirect('n_detalles_viaje', idV=idV)

    if viaje.flg_confirmacion_auto:
        if viaje.numero_asientos_libres > 0:
            viaje.numero_asientos_libres = F("numero_asientos_libres") - 1
            viaje.save()
            plaza_aceptada = Plazas(id_persona=persona, id_viaje=viaje, flg_conductor=False, estado=2,
                                    fechor_confirmado=dateNow)
            plaza_aceptada.save()
            messages.success(request, "¡¡¡Reserva registrada correctamente!!!<br>\
                                       ¡¡¡Avisaremos al usuario de que has aceptado su petición!!!")
        else:
            # se ha quedado sin plaza por reserva de otra de forma simultanea
            messages.error(request, "¡¡¡Lo siento, se han agotado las plazas de este viaje en el último momento!!!")
            messages.error(request, "¡¡¡Prueba en otro viaje!!!")
    else:
        plaza_pendiente = Plazas(id_persona=persona, id_viaje=viaje, flg_conductor=False, estado=1,
                                 fechor_pendiente=dateNow)
        plaza_pendiente.save()
        messages.success(request, "¡¡¡Tu solicitud de reserva se ha enviado al conductor!!! Tendrás tu plaza reservada en cuanto sea aceptada.")

        viaje_plaza_pendiente = Viajes.objects.filter(id=idV)
        # Enviar Mail de aviso al conductor del viaje
        fechor_ida = (viaje_plaza_pendiente.values_list('fechor_ida', flat=True)[0]).date()
        ciudad_origen = viaje_plaza_pendiente.values_list('ciudad_origen', flat=True)[0]
        ciudad_destino = viaje_plaza_pendiente.values_list('ciudad_destino', flat=True)[0]
        to_email_plazas_list = viaje_plaza_pendiente.values_list('id_persona__id_usuario__email', flat=True)
        mail_asunto = "RESERVAS PENDIENTES DE ACEPTAR!!!"
        mail_mensaje = (f""
                        f"Tienes reservas pendientes de gestionar en tu viaje del día {fechor_ida} de {ciudad_origen} hasta {ciudad_destino}.\n"
                        f"Entra en tu portal y accede a MIS VIAJES para gestionar las reservas.\n "
                        )
        if len(to_email_plazas_list) > 0:
            enviarEmail_alertas(request, request.user, to_email_plazas_list, mail_asunto, mail_mensaje, "")

    return redirect('n_detalles_viaje', idV=idV)

@check_logued_usuario
def v_aceptar_pasajero(request, idV, idPl):
    dateNow = timezone.now()
    viaje = Viajes.objects.get(id=idV)
    asientos_libres = viaje.numero_asientos_libres
    if asientos_libres > 0:
        viaje.numero_asientos_libres = F("numero_asientos_libres") - 1
        viaje.save()
        asientos_libres = asientos_libres-1
        plaza_aceptada = Plazas.objects.filter(id=idPl, id_viaje=idV)
        plaza_aceptada.update(estado=2, fechor_confirmado=dateNow)
        messages.success(request, "¡¡¡Reserva registrada correctamente!!!")

        # Enviar Mail de aviso al pasajero aceptado
        fechor_ida = (plaza_aceptada.values_list('id_viaje__fechor_ida', flat=True)[0]).date()
        ciudad_origen = plaza_aceptada.values_list('id_viaje__ciudad_origen', flat=True)[0]
        ciudad_destino = plaza_aceptada.values_list('id_viaje__ciudad_destino', flat=True)[0]
        to_email_plazas_list = plaza_aceptada.values_list('id_persona__id_usuario__email', flat=True)
        mail_asunto = "RESERVA ACEPTADA!!!"
        mail_mensaje = (f""
                        f"¡Felicidades!\n"
                        f"El conductor ha aceptado tu plaza en el viaje el día {fechor_ida} de {ciudad_origen} hasta {ciudad_destino}.\n"
                        f"Entra en tu portal y accede a los detalles del viaje y ponte en contacto con el conductor.\n "
                        f"Disfruta del viaje!!!"
                        )
        alerta_mensaje = f"¡¡¡Avisaremos al usuario de que has aceptado su petición!!!"
        if len(to_email_plazas_list) > 0:
            enviarEmail_alertas(request, request.user, to_email_plazas_list, mail_asunto, mail_mensaje, alerta_mensaje)

        # Si se han cubierto todas las plazas, cancelamos todas las reservas pendientes y avisamos por mail a los afectados
        if asientos_libres == 0:
            print(snanananass111)
            plazas_rechazadas_viaje_lleno = Plazas.objects.filter(id_viaje=idV, estado=1)
            to_email_plazas_list = plazas_rechazadas_viaje_lleno.values_list('id_persona__id_usuario__email', flat=True)
            mail_asunto = "RESERVA RECHAZADA POR VIAJE COMPLETO!!!"
            mail_mensaje = (f""
                            f"¡Se ha llenado el viaje y no has conseguido plaza!\n"
                            f"El conductor ha aceptado todas las plazas en el viaje el día {fechor_ida} de {ciudad_origen} hasta {ciudad_destino}.\n"
                            f"Entra en tu portal encuentra otro viaje similar.\n "
                            f"No pierdas la esperanza :) !!!"
                            )
            alerta_mensaje = f"¡¡¡El viaje está completo, avisaremos a los usuarios pendientes de que el viaje está completo!!!"
            if len(to_email_plazas_list) > 0:
                enviarEmail_alertas(request, request.user, to_email_plazas_list, mail_asunto, mail_mensaje,
                                    alerta_mensaje)
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
    plaza_rechazada = Plazas.objects.filter(id=idPl, id_viaje=idV)
    plaza_rechazada.update(estado=3, fechor_rechazado=dateNow)

    # Extraer de QerySet el valor de un campo
    fechor_ida = (plaza_rechazada.values_list('id_viaje__fechor_ida', flat=True)[0]).date()
    ciudad_origen = plaza_rechazada.values_list('id_viaje__ciudad_origen', flat=True)[0]
    ciudad_destino = plaza_rechazada.values_list('id_viaje__ciudad_destino', flat=True)[0]
    to_email_plazas_list = plaza_rechazada.values_list('id_persona__id_usuario__email', flat=True)
    mail_asunto = "RESERVA RECHAZADA!!!"
    mail_mensaje = (f""
                    f"¡Lo sentimos!\n"
                    f"El conductor ha rechazado tu reserva del viaje el día {fechor_ida} de {ciudad_origen} hasta {ciudad_destino}.\n"
                    f"Entra en tu portal y busca otro viaje similar.\n\nLa esperanza es lo último que se pierde :)"
                    )
    alerta_mensaje = f"Hemos notificado al pasajero de la reserva rechazada."
    if len(to_email_plazas_list) > 0:
        enviarEmail_alertas(request, request.user, to_email_plazas_list, mail_asunto, mail_mensaje, alerta_mensaje)

    return redirect('n_detalles_viaje', idV=idV)

@check_logued_usuario
def v_cancelar_reserva(request, idV, idPl):
    dateNow = timezone.now()
    plaza_cancelada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado=4, fechor_cancelado=dateNow)

    messages.success(request, "¡¡¡Has cancelado tu reserva en este viaje!!!")

    return redirect('n_detalles_viaje', idV=idV)

@check_logued_usuario
def v_plaza_finalizada(request, idV, idPl):
    dateNow = timezone.now()
    if idPl == 0: # Significa Conductor
        plaza_finalizada = Plazas.objects.filter(flg_conductor=True, id_viaje=idV).update(estado_plaza_viaje=3)
    else:
        plaza_finalizada = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado_plaza_viaje=3)

    messages.success(request, "¡¡¡Gracias por confirmar el viaje!!!")

    return redirect('n_detalles_viaje', idV=idV)

@check_logued_usuario
def v_plaza_problematica(request, idV, idPl):
    dateNow = timezone.now()
    if idPl == 0: # Significa Conductor
        plaza_problematica = Plazas.objects.filter(flg_conductor=True, id_viaje=idV).update(estado_plaza_viaje=4)
    else:
        plaza_problematica = Plazas.objects.filter(id=idPl, id_viaje=idV).update(estado_plaza_viaje=4)

    messages.success(request, "¡¡¡Hemos registrado tu notificación de Viaje Problemático!!!")
    messages.success(request, "¡¡¡Contacta con nosotros para darnos más detalles del problema!!!")

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
                                                        ,'id', 'ciudad_destino', 'fechor_ida'
                                                        ,'importe_total_asiento', 'fechor_llegada'
                                                        ,'numero_asientos_libres', 'flg_confirmacion_auto'
                                                        ,'estado', 'id_persona_id__pref_conversacion'
                                                        ,'id_persona_id__pref_fumar', 'id_persona_id__imagen'
                                                        ,'distancia_kms','duracion_min') \
        .annotate(
            count_opiniones=Subquery(Opiniones.objects.filter(crit1).values('id_persona_receptor')
                                     .annotate(c=Count('*')).values('c')),
            avg_puntuacion=Subquery(Opiniones.objects.filter(crit1).values('id_persona_receptor')
                                    .annotate(avg=Avg('puntuacion')).values('avg'))
                ).filter(ciudad_origen=origen, ciudad_destino=destino, fechor_ida__date=fecha).order_by('fechor_ida')

    fV = BuscarViajeFilter(request.POST, queryset=Usuario_Viajes_Opiniones)
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
        google_account_values = request.session.get('google_initial_values')
        if google_account_values:
            messages.success(request, "¡¡¡Se han recogido los datos de tu cuenta, solo falta completar el resto!!!")
            form = PersonasForm(None, initial=google_account_values)
        else:
            form = PersonasForm()
        return render(request, 'nuevo_usuario.html', {'form': form})


@check_logued_usuario
@get_persona_usuario
@get_vehiculos_usuario
def v_nuevo_viaje(request, persona, vehiculos):
    if not vehiculos:
        messages.error(request, "¡¡¡Por favor, registra 1 vehiculo antes de publicar viajes!!!.")
        return redirect('n_menu_usuario_coches')

    localizaciones = Localizaciones.objects.all()

    args = {
        "usuario": persona,
        "localizaciones": localizaciones
    }

    if request.method == "POST":
        form = ViajesForm(request.POST, user=request.user)
        vueltaform = VueltaViajesForm(request.POST)
        if form.is_valid() and vueltaform.is_valid():
            viaje = form.save(commit=False)
            v_fechor_ida = datetime.combine(viaje.fecha_ida, viaje.hora_ida)
            viaje.id_persona = persona
            viaje.numero_asientos_libres = viaje.numero_asientos_viaje
            viaje.importe_comision_asiento = viaje.importe_conductor_asiento/10
            viaje.importe_total_asiento = viaje.importe_comision_asiento + viaje.importe_conductor_asiento
            viaje.fechor_ida = v_fechor_ida
            viaje.id_vehiculo = viaje.id_vehiculo
            viaje.fechor_pendiente = timezone.now()
            # Tiempo y Distancia viaje
            geo = Geolocalizacion()
            kms_viaje, minutos_viaje = geo.calcular_parametros_conduccion(viaje.ciudad_origen, viaje.ciudad_destino)
            viaje.distancia_kms = kms_viaje
            viaje.duracion_min = minutos_viaje
            viaje.fechor_llegada = v_fechor_ida + timedelta(minutes=minutos_viaje)

            # Pasamos validaciones sobre el viaje de Ida
            val = ValidacionesViajes(persona_input=persona, viaje_input=viaje)
            lista_mensajes = val.val_mensajes_salida()
            for mensaje in lista_mensajes:
                messages.error(request, mensaje)
            if lista_mensajes:
                return redirect('n_nuevo_viaje')

            if form.cleaned_data['flg_ida_vuelta']:
                v_fechor_vuelta = datetime.combine(vueltaform.cleaned_data['fecha_vuelta'], vueltaform.cleaned_data['hora_vuelta'])
                viaje_vuelta = Viajes()
                viaje_vuelta.id_persona = persona
                viaje_vuelta.id_vehiculo = viaje.id_vehiculo
                viaje_vuelta.numero_asientos_viaje = vueltaform.cleaned_data['numero_asientos_vuelta']
                viaje_vuelta.numero_asientos_libres = vueltaform.cleaned_data['numero_asientos_vuelta']
                viaje_vuelta.ciudad_origen = vueltaform.cleaned_data['ciudad_origen_vuelta']
                viaje_vuelta.ciudad_destino = vueltaform.cleaned_data['ciudad_destino_vuelta']
                viaje_vuelta.fecha_ida = vueltaform.cleaned_data['fecha_vuelta']
                viaje_vuelta.hora_ida = vueltaform.cleaned_data['hora_vuelta']
                viaje_vuelta.importe_conductor_asiento = vueltaform.cleaned_data['importe_conductor_asiento_vuelta']
                viaje_vuelta.importe_comision_asiento = viaje_vuelta.importe_conductor_asiento / 10
                viaje_vuelta.importe_total_asiento = viaje_vuelta.importe_comision_asiento + viaje_vuelta.importe_conductor_asiento
                viaje_vuelta.fechor_ida = v_fechor_vuelta
                viaje_vuelta.fechor_pendiente = timezone.now()
                viaje_vuelta.distancia_kms = kms_viaje
                viaje_vuelta.duracion_min = minutos_viaje
                viaje_vuelta.fechor_llegada = v_fechor_vuelta + timedelta(minutes=minutos_viaje)
                viaje_vuelta.flg_ida_vuelta = True
                # Pasamos validaciones sobre el viaje de Vuelta
                val = ValidacionesViajes(persona_input=persona, viaje_input=viaje_vuelta)
                lista_mensajes = val.val_mensajes_salida()
                for mensaje in lista_mensajes:
                    messages.error(request, "(Viaje de Vuelta)" + mensaje)
                if lista_mensajes:
                    return redirect('n_nuevo_viaje')
            # Al pasar todas las validaciones guardamos los viajes:
            # Guardamos el VIAJE
            viaje.save()
            # Insertamos la plaza del conductor
            plaza_conductor = Plazas(id_persona=persona, id_viaje=viaje, flg_conductor=True, estado=2)
            plaza_conductor.save()
            messages.success(request, "¡¡¡Viaje publicado correctamente!!!")
            if form.cleaned_data['flg_ida_vuelta']:
                # Guardamos el VIAJE de VUELTA
                viaje_vuelta.save()
                # Insertamos la plaza del conductor
                plaza_conductor_vuelta = Plazas(id_persona=persona, id_viaje=viaje_vuelta, flg_conductor=True, estado=2)
                plaza_conductor_vuelta.save()
                messages.success(request, "¡¡¡Y también hemos publicado el viaje de vuelta!!!")

            return redirect('n_pagina_principal')
        else:
            messages.error(request, "¡¡¡ERROR. Viaje no publicado!!!.")
            return redirect('n_pagina_principal')
    else:
        form = ViajesForm(user=request.user)
        vueltaform = VueltaViajesForm()
        args.update({'form': form, 'vueltaform': vueltaform})
        return render(request, 'nuevo_viaje.html', args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_perfil(request, persona):
    args = {
            "usuario": persona
            }
    if request.method == "POST":
        form = PersonasForm(request.POST, request.FILES, instance=persona)
        if form.is_valid():
            persona_form = form.save()
            persona_form.save()
            messages.success(request, "¡¡¡Datos de Usuario actualizados correctamente!!!")
            return redirect('n_menu_usuario_perfil')
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!!")
            return redirect('n_menu_usuario_perfil')
    else:
        # Se crea un form con la información del usuario logueado
        form = PersonasForm(instance=persona)
        args.update({"form": form})
        return render(request, 'menu_usuario_perfil.html', args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_coches(request, persona):
    try:
        vehiculos = Vehiculos.objects.filter(id_persona=persona)
    except Vehiculos.DoesNotExist:
        vehiculos = None

    args = {
            "usuario": persona,
            "vehiculos": vehiculos
            }

    if request.method == "POST":
        form = VehiculosForm(request.POST, request.FILES)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.id_persona = persona
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
    viajes_pend_count = Viajes.objects.filter(Q(id_vehiculo=vehiculo, estado=1)).count()
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
            #print(vehiculoform.imagen_vehiculo)
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
def v_menu_usuario_preferencias(request, persona):
    args = {
        "usuario": persona
    }
    if request.method == "POST":
        persona.pref_conversacion = request.POST['pref_conversacion']
        persona.pref_musica = request.POST['pref_musica']
        persona.pref_mascota = request.POST['pref_mascota']
        persona.pref_fumar = request.POST['pref_fumar']
        persona.pref_comida = request.POST['pref_comida']
        persona.save()
        messages.success(request, "¡¡¡Preferencias actualizadas correctamente!!!")
        return redirect('n_menu_usuario_preferencias')
    else:
        return render(request, 'menu_usuario_preferencias.html', args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_caparazon(request, persona):
    try:
        usuarioCaparazon = Caparazones.objects.get(id_persona=persona)
    except Caparazones.DoesNotExist:
        # si no existe el caparazon del usuario, se crea uno en blanco
        usuarioCaparazon = Caparazones(id_persona=persona)
        usuarioCaparazon.save()

    args = {
            "usuario": persona,
            "usuarioCaparazon": usuarioCaparazon
            }

    if request.method == "POST":
        form = CaparazonesForm(request.POST, instance=usuarioCaparazon)
        if form.is_valid():
            caparazon = form.save()
            caparazon.save()
            messages.success(request, "¡¡¡Los datos de tu Caparazón se han actualizado correctamente!!!")
            return redirect('n_menu_usuario_caparazon')
        else:
            messages.error(request, "¡¡¡ERROR. Los datos no se han actualizado!!!")
            return redirect('n_menu_usuario_caparazon')
    else:
        # Se crea un form con la información del usuario logueado
        form = CaparazonesForm(instance=usuarioCaparazon)
        args.update({"form": form})
        return render(request, 'menu_usuario_caparazon.html', args)


@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_opiniones(request, persona):

    # Se actualizan los mensajes como leidos
    Opiniones.objects.filter(id_persona_receptor=persona).update(flg_leido=True)

    opiniones_recibidas = Opiniones.objects.filter(id_persona_receptor=persona)
    opiniones_publicadas = Opiniones.objects.filter(id_persona_publicador=persona)


    # Se crea un diccionario con las categorias de opiniones y su valor
    opiniones_cat_dict = dict()
    for x in reversed(range(len(categorias_puntuacion))):  # de 0 a 4 (5 iteraciones)
        categoria = categorias_puntuacion[x][1]
        count_opiniones = opiniones_recibidas.filter(categoria_puntuacion=(x+1)).count()
        opiniones_cat_dict.update({categoria: count_opiniones})

    avg_puntuacion = opiniones_recibidas.aggregate(avg_punt=Avg('puntuacion'))
    total_opiniones = opiniones_recibidas.count()

    args = {
            "usuario": persona,
            "opiniones_recibidas": opiniones_recibidas,
            "opiniones_publicadas": opiniones_publicadas,
            "avg_puntuacion": avg_puntuacion,
            "total_opiniones": total_opiniones,
            "opiniones_cat_dict": opiniones_cat_dict
    }
    return render(request, 'menu_usuario_opiniones.html', args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_notificaciones(request, persona):

    args = {
        "usuario": persona
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

        persona.notif_noticiasofertas = notif_noticiasofertas
        persona.notif_opiniones = notif_opiniones
        persona.notif_reservas = notif_reservas
        persona.save()
        messages.success(request, "¡¡¡Notificaciones actualizadas correctamente!!!")
        return redirect('n_menu_usuario_notificaciones')
    else:
        return render(request, 'menu_usuario_notificaciones.html', args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_pagoscobros(request, persona):

    args = {
            "usuario": persona
            }

    return render(request, 'menu_usuario_pagoscobros.html', args)

@check_logued_usuario
@get_persona_usuario
def v_menu_usuario_contrasenya(request, persona):
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
        'usuario': persona,
        'form': form
    }
    return render(request, 'menu_usuario_contrasenya.html', args)

@check_logued_usuario
@get_persona_usuario
def v_perfil_publico(request, idP, persona):

    usuario_perfil = Personas.objects.get(id=idP)
    try:
        caparazon = Caparazones.objects.filter(id_persona=usuario_perfil)
    except caparazon.DoesNotExist:
        caparazon = None

    try:
        vehiculo = Vehiculos.objects.filter(id_persona=usuario_perfil).first()
    except vehiculo.DoesNotExist:
        vehiculo = None

    try:
        viajesConductor = Viajes.objects.filter(id_persona=usuario_perfil)
    except viajesConductor.DoesNotExist:
        viajesConductor = None

    try:
        reservasPasajero = Plazas.objects.filter(id_persona=usuario_perfil)
    except reservasPasajero.DoesNotExist:
        reservasPasajero = None

    try:
        opiniones_recibidas = Opiniones.objects.filter(id_persona_receptor=usuario_perfil)
    except opiniones_recibidas.DoesNotExist:
        opiniones_recibidas = None
    total_viajesConductor = viajesConductor.count()
    total_viajesConductor_Canc = viajesConductor.filter(estado=3).count()
    total_viajesPasajero = reservasPasajero.filter(estado=2).count()
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
        "usuario": persona,
        "usuario_perfil": usuario_perfil,
        "caparazon": caparazon,
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
def v_mis_viajes(request, persona):

    idP = persona.id

    try:
        crit1 = Q(
            id_persona_publicador=idP,
            id_viaje=OuterRef('id'),
            id_viaje__estado=2  # Viaje Realizado
        )

        plazas = Plazas.objects.filter(Q(id_persona=persona) & (~Q(estado=3))).values('id_viaje')  #excluye plazas rechazadas
        listado_viajes = (Viajes.objects.annotate(count_opiniones=Subquery(
                                    Opiniones.objects.filter(crit1).values('id').annotate(c=Count('*')).values('c')
                                            ))
                          .filter(id__in=plazas.values_list('id_viaje')).order_by('-fechor_ida'))
        listado_viajes_distinct = listado_viajes.distinct()
        print(listado_viajes)

        listado_plazas_viajes = (Plazas.objects\
            .values('id_viaje__id','id_persona__id','id_persona__imagen','id_persona__nombre','flg_conductor')\
            .filter(id_viaje__in=listado_viajes_distinct).order_by('-flg_conductor').distinct())


    except plazas.DoesNotExist:
        listado_viajes = None
        listado_plazas_viajes = None

    fV = MisViajesFilter(request.GET, queryset=listado_viajes)
    args = {
        "usuario": persona,
        "idP": idP,
        "filter": fV,
        "listado_plazas_viajes": listado_plazas_viajes
    }

    return render(request, 'mis_viajes.html', args)

@check_logued_usuario
@get_persona_usuario
def v_mis_mensajes(request, persona):

    idP = persona.id

    #listado_conversaciones = Mensajes.objects.filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario)).values_list('id_persona_publicador','id_persona_receptor').distinct()
    #listado_conversaciones = Mensajes.objects.filter(Q(id_persona_publicador=usuario) | Q(id_persona_receptor=usuario))

    # Se actualizan los mensajes como leidos
    Mensajes.objects.filter(id_persona_receptor=persona).update(flg_leido=True)


    listado_conversaciones = Mensajes.objects.values('id_persona_publicador__nombre', 'id_persona_publicador__apellido1', 'id_persona_publicador__id', 'id_persona_publicador__imagen'
                                                        , 'id_persona_receptor__nombre', 'id_persona_receptor__apellido1', 'id_persona_receptor__id', 'id_persona_receptor__imagen'
                                                        )\
        .annotate(max_fec_created=Max('fec_created'))\
        .filter(Q(id_persona_publicador=persona) | Q(id_persona_receptor=persona))
    #print(listado_conversaciones.count())
    fM = MensajesFilter(request.GET, queryset=listado_conversaciones)

    args = {
            "usuario": persona,
            "idP": idP,
            "filter": fM
            }

    return render(request, "mis_mensajes.html", args)

@check_logued_usuario
@get_persona_usuario
def v_conversacion(request, idPc, persona):

    idP = persona.id

    usuario_receptor = Personas.objects.get(id=idPc)
    listado_mensajes = Mensajes.objects.filter(Q(id_persona_publicador=persona, id_persona_receptor=usuario_receptor) |
                                               Q(id_persona_publicador=usuario_receptor, id_persona_receptor=persona)).order_by('fec_created')

    args = {
            "usuario": persona,
            "idP": idP,
            "usuario_receptor": usuario_receptor,
            "listado_mensajes": listado_mensajes
            }
    if request.method == "POST":
        mensaje = request.POST.get('mensaje', False)
        # Codificamos el mensaje para evitar palabrotas
        mensaje_limpio = codificar_numeros(mensaje)
        # Insertamos el mensaje
        nuevo_mensaje = Mensajes(id_persona_publicador=persona, id_persona_receptor=usuario_receptor, flg_leido=False, mensaje=mensaje_limpio)
        nuevo_mensaje.save()
        return render(request, "conversacion.html", args)
    else:
        return render(request, "conversacion.html", args)

@check_logued_usuario
@get_persona_usuario
def v_opiniones_recibidas_main(request, idPr, persona):

    usuario_receptor = Personas.objects.get(id=idPr)

    try:
        opiniones_recibidas = Opiniones.objects.filter(id_persona_receptor=usuario_receptor)
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
        "usuario": persona,
        "avg_puntuacion": avg_puntuacion,
        "total_opiniones": total_opiniones,
        "opiniones_recibidas": opiniones_recibidas,
        "opiniones_cat_dict": opiniones_cat_dict
    }

    return render(request, 'opiniones_recibidas_main.html', args)

@check_logued_usuario
@get_persona_usuario
def v_nueva_opinion (request, idV, idPr, idO, persona):

    viaje = Viajes.objects.get(id=idV)
    persona_receptor = Personas.objects.get(id=idPr)
    datos = {
        "usuario": persona,
        "persona_receptor": persona_receptor,
    }
    if request.method == "POST":
        if idO != 0:  # si el argumento idOpinion es informado es porque se va a insertar una respuesta de esa idOpinion
            Opiniones.objects.filter(id=idO).update(flg_opinion_respondida=True)
            opinion_respuesta = Opiniones.objects.get(id=idO)
        else:
            opinion_respuesta = None

        rating = int(request.POST.get("rating"))
        opinion = request.POST.get("opinion")
        # Se inserta la opinión
        nueva_opinion = Opiniones(id_persona_publicador=persona,
                                  id_persona_receptor=persona_receptor,
                                  id_viaje=viaje,
                                  puntuacion=rating,
                                  categoria_puntuacion=rating,
                                  mensaje_opinion=opinion,
                                  id_opinion_respuesta=opinion_respuesta,
                                  fechor_opinion=datetime.now()
                                  )
        nueva_opinion.save()
        messages.success(request, "¡¡¡Muchas gracias!!! Se ha publicado tu reseña!!!")
        return render(request, "pagina_principal.html", datos)

    return render(request, "nueva_opinion.html", datos)

@check_logued_usuario
def v_contacto(request):

    if request.method == "POST":
        email = request.POST.get("email2")
        asunto = "Contacto: " + request.POST.get("subject")
        mensaje = f"Mensaje de {email}: \n\n" + request.POST.get("message")
        try:
            send_mail(asunto,
                      mensaje,
                      email,
                      ["muvil.group@gmail.com"] #Destinatario puede ser distinto al mail configurado en settings.py
                      )
            return redirect("/contacto/?valido")
        except:
            return redirect("/contacto/?error")

    datos = {

    }
    return render(request, "contacto.html", datos)

def custom_redirect_after_login(request):
    next_url = request.GET.get('next')

    if request.META.get('HTTP_X_FROM_APP') == 'true':
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if "iphone" in user_agent or "ios" in user_agent:
            return redirect("muvil://")

    return redirect(next_url if next_url else "/")
