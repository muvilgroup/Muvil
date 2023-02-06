from django.db import models
from .choices import genero, tipo_vehiculo, prestigio

# Create your models here.

class Personas (models.Model):
    nombre = models.CharField(max_length=64)
    apellido1 = models.CharField(max_length=64)
    apellido2 = models.CharField(max_length=64, blank=True, null=True)
    fec_nacimiento = models.DateField(blank=True, null=True)
    tipo_documento = models.CharField (max_length=8)
    numero_documento = models.CharField(max_length=32)
    email = models.CharField(max_length=320)
    numero_telefono = models.PositiveIntegerField()
    genero = models.CharField(max_length=1, choices=genero, default='F', blank=True, null=True)
    password = models.CharField(max_length=30, default='<NO_PASSWORD>')
    puntuacion = models.DecimalField(max_digits=2, decimal_places=1, default=3.5, blank=True, null=True)
    prestigio = models.CharField(max_length=2, choices=prestigio, default='B', blank=True, null=True)
    numero_opiniones = models.PositiveIntegerField(default = '0', blank=True, null=True)
    ruta_foto = models.CharField(max_length=32,default='img/avatar-mujer.jpg', blank=True, null=True)
    descripcion = models.CharField(max_length=3000, blank=True, null=True)
    imagen = models.ImageField(upload_to='images/users_profile', blank=True, null=True)



class Vehiculos (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id',null=True,blank=True,on_delete=models.CASCADE)
    tipo_vehiculo =  models.CharField(max_length=1, choices=tipo_vehiculo, default='C')
    marca = models.CharField(max_length=64)
    modelo = models.CharField(max_length=64)
    color = models.CharField(max_length=12)
    años_antiguedad = models.PositiveIntegerField()
    numero_asientos = models.PositiveIntegerField()
    flag_acepta_fumador = models.BooleanField(default=False)
    flag_acepta_mascota = models.BooleanField(default=False)


class Viajes(models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id',null=True,blank=True,on_delete=models.CASCADE)
    ciudad_origen = models.CharField(max_length=64)
    ciudad_destino = models.CharField(max_length=64)
    flg_ida_vuelta = models.BooleanField(default=False)
    fecha_ida = models.DateField()
    fecha_vuelta = models.DateField()
    numero_asientos_viaje = models.PositiveSmallIntegerField()
    flg_solicitado = models.BooleanField(default=False)
    flg_reservado = models.BooleanField(default=False)
    flg_cancelado = models.BooleanField(default=False)
    flg_incidencia = models.BooleanField(default=False)
    importe_total_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    importe_comision_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    importe_conductor_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    numero_asientos_libres = models.PositiveIntegerField(default=0)
    hora_ida = models.TimeField(default="00:00")
    hora_vuelta = models.TimeField(default="00:00")
