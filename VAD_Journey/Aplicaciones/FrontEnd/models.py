from django.db import models
from .choices import genero, tipo_vehiculo, prestigio, categorias_puntuacion, estados_transferencias, estados_viajes, estados_plazas
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime

# Create your models here.

class Personas (models.Model):
    nombre = models.CharField(max_length=64)
    apellido1 = models.CharField(max_length=64)
    apellido2 = models.CharField(max_length=64, blank=True, null=True)
    fec_nacimiento = models.DateField(blank=True, null=True)
    tipo_documento = models.CharField (max_length=8)
    numero_documento = models.CharField(max_length=32)
    email = models.CharField(max_length=320)
    numero_telefono = models.PositiveIntegerField(validators=[MaxValueValidator(999999999)])
    genero = models.CharField(max_length=1, choices=genero, default='F', blank=True, null=True)
    password = models.CharField(max_length=30, default='<NO_PASSWORD>')
    puntuacion = models.DecimalField(max_digits=2, decimal_places=1, default=3.5, blank=True, null=True)
    prestigio = models.CharField(max_length=2, choices=prestigio, default='B', blank=True, null=True)
    numero_opiniones = models.PositiveIntegerField(default = '0', blank=True, null=True)
    descripcion = models.CharField(max_length=3000, blank=True, null=True)
    imagen = models.ImageField(upload_to='images/users_profile', default="images/users_profile/avatar-mujer.jpg")
    pref_conversacion = models.PositiveIntegerField(default='1')
    pref_musica = models.PositiveIntegerField(default='1')
    pref_mascota = models.PositiveIntegerField(default='1')
    pref_fumar = models.PositiveIntegerField(default='1')
    pref_comida = models.PositiveIntegerField(default='1')
    notif_noticiasofertas = models.PositiveIntegerField(default='3')
    notif_opiniones = models.PositiveIntegerField(default='3')
    notif_reservas = models.PositiveIntegerField(default='3')
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'personas'
        verbose_name_plural = 'personas'
    def __str__(self):
        return str(self.id) + ' - ' + self.email

class Vehiculos (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id',null=True,blank=True,on_delete=models.CASCADE)
    tipo_vehiculo =  models.CharField(max_length=1, choices=tipo_vehiculo, default='C')
    marca = models.CharField(max_length=64)
    modelo = models.CharField(max_length=64)
    color = models.CharField(max_length=12)
    anyo_antiguedad = models.PositiveIntegerField()
    numero_asientos = models.PositiveIntegerField()
    flag_acepta_fumador = models.BooleanField(default=False)
    flag_acepta_mascota = models.BooleanField(default=False)
    matricula = models.CharField(max_length=8, default='0000XXXX')
    imagen_vehiculo = models.ImageField(upload_to='images/vehicles', default="images/vehicles/default-car.jpeg")
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'vehiculos'
        verbose_name_plural = 'vehiculos'
    def __str__(self):
        return str(self.id) + ' - ' + self.marca + ' ' + self.modelo

class Viajes (models.Model):
    id_persona = models.ForeignKey(Personas, to_field='id', on_delete=models.CASCADE)
    ciudad_origen = models.CharField(max_length=64)
    ciudad_destino = models.CharField(max_length=64)
    flg_ida_vuelta = models.BooleanField(default=False)
    fecha_ida = models.DateField(blank=True, null=True)
    fecha_vuelta = models.DateField(blank=True, null=True)
    numero_asientos_viaje = models.PositiveSmallIntegerField()
    '''flg_solicitado = models.BooleanField(default=False)
    flg_reservado = models.BooleanField(default=False)
    flg_cancelado = models.BooleanField(default=False)
    flg_incidencia = models.BooleanField(default=False)'''
    estado = models.PositiveIntegerField(choices=estados_viajes, default=1)
    importe_total_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    importe_comision_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    importe_conductor_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    numero_asientos_libres = models.PositiveIntegerField(default=0)
    hora_ida = models.TimeField()
    hora_vuelta = models.TimeField(blank=True, null=True)
    fechor_ida = models.DateTimeField()
    fechor_vuelta = models.DateTimeField(blank=True, null=True)
    id_vehiculo = models.ForeignKey(Vehiculos, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'viajes'
        verbose_name_plural = 'viajes'

class Opiniones (models.Model):
    id_persona_publicador = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE, related_name='id_publicador')
    id_persona_receptor = models.ForeignKey(Personas, to_field='id', on_delete=models.CASCADE, related_name='id_receptor')
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    puntuacion = models.DecimalField(max_digits=2, decimal_places=1, default=3.5)
    categoria_puntuacion = models.PositiveIntegerField(choices=categorias_puntuacion, default=3)
    mensaje_opinion = models.CharField(max_length=3000, blank=True, null=True)
    flg_respuesta = models.BooleanField(default=False)
    mensaje_respuesta = models.CharField(max_length=3000, blank=True, null=True)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'opiniones'
        verbose_name_plural = 'opiniones'

class Plazas (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE)
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    '''flg_solicitado = models.BooleanField(default=False)
    flg_reservado = models.BooleanField(default=False)
    flg_cancelado = models.BooleanField(default=False)
    flg_incidencia = models.BooleanField(default=False)'''
    flg_conductor = models.BooleanField(default=False)
    estado = models.PositiveIntegerField(choices=estados_plazas, default=1)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'plazas'
        verbose_name_plural = 'plazas'

class Transferencias (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE)
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    importe = models.DecimalField(max_digits = 5,decimal_places = 2, default=0.0)
    estado = models.PositiveIntegerField(choices=estados_transferencias, default=1)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'transferencias'
        verbose_name_plural = 'transferencias'

class MetodosPago (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE)
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    importe = models.DecimalField(max_digits = 5,decimal_places = 2, default=0.0)
    estado = models.PositiveIntegerField(choices=estados_transferencias, default=1)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'transferencias'
        verbose_name_plural = 'transferencias'

class Mensajes (models.Model):
    id_persona_publicador = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE, related_name='id_publicador_m')
    id_persona_receptor = models.ForeignKey(Personas, to_field='id', on_delete=models.CASCADE, related_name='id_receptor_m')
    #id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=3000, blank=True, null=True)
    flg_leido = models.BooleanField(default=False)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'mensajes'
        verbose_name_plural = 'mensajes'

