from django.db import models
from .choices import genero, tipo_vehiculo, prestigio, categorias_puntuacion, estado_transferencia, estados_viajes, \
    estados_plazas, equipaje, tipo_transferencia, tipo_descuento
from ..users.models import Usuario
from django.core.validators import RegexValidator

class Personas (models.Model):
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")

    id_usuario = models.ForeignKey(Usuario, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=64, blank=False, null=False)
    apellido1 = models.CharField(max_length=64, blank=False, null=False)
    apellido2 = models.CharField(max_length=64, blank=True, null=True)
    fec_nacimiento = models.DateField(blank=False, null=False)
    tipo_documento = models.CharField (max_length=8, blank=False, null=False)
    numero_documento = models.CharField(max_length=32, blank=False, null=False, unique=True)
    num_telefono = models.CharField(validators = [phoneNumberRegex], max_length = 16, blank=False, null=False)
    genero = models.CharField(max_length=1, choices=genero, default='F', blank=True, null=True)
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
        return str(self.id) + ' - ' + self.nombre

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
        #return str(self.id) + ' - ' + self.marca + ' ' + self.modelo
        return self.marca + ' ' + self.modelo

class Viajes (models.Model):
    id_persona = models.ForeignKey(Personas, to_field='id', on_delete=models.CASCADE)
    ciudad_origen = models.CharField(max_length=64)
    ciudad_destino = models.CharField(max_length=64)
    fecha_ida = models.DateField(blank=True, null=True)
    numero_asientos_viaje = models.PositiveSmallIntegerField()
    equipaje = models.CharField(max_length=2, choices=equipaje, default='EM')
    flg_confirmacion_auto = models.BooleanField(default=True)
    estado = models.PositiveIntegerField(choices=estados_viajes, default=1)
    importe_total_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    importe_comision_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    importe_conductor_asiento = models.DecimalField(max_digits = 5,decimal_places = 2)
    numero_asientos_libres = models.PositiveIntegerField(default=0)
    hora_ida = models.TimeField()
    fechor_ida = models.DateTimeField()
    fechor_pendiente = models.DateTimeField(blank=True, null=True)
    fechor_realizado = models.DateTimeField(blank=True, null=True)
    fechor_cancelado = models.DateTimeField(blank=True, null=True)
    id_vehiculo = models.ForeignKey(Vehiculos, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    flg_ida_vuelta = models.BooleanField(default=False)
    distancia_kms = models.DecimalField(max_digits=6, decimal_places=1)
    duracion_min = models.PositiveIntegerField()
    fechor_llegada = models.DateTimeField()
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'viajes'
        verbose_name_plural = 'viajes'

class Opiniones (models.Model):
    id_persona_publicador = models.ForeignKey(Personas, to_field='id', on_delete=models.CASCADE, related_name='id_publicador')
    id_persona_receptor = models.ForeignKey(Personas, to_field='id', on_delete=models.CASCADE, related_name='id_receptor')
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    puntuacion = models.DecimalField(max_digits=2, decimal_places=1, default=3.5)
    categoria_puntuacion = models.PositiveIntegerField(choices=categorias_puntuacion, default=3)
    mensaje_opinion = models.CharField(max_length=3000, blank=True, null=True)
    fechor_opinion = models.DateTimeField(blank=True, null=True)
    flg_leido = models.BooleanField(default=False)
    flg_opinion_respondida = models.BooleanField(default=False)
    id_opinion_respuesta = models.ForeignKey('self', to_field='id', on_delete=models.CASCADE, blank=True, null=True)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'opiniones'
        verbose_name_plural = 'opiniones'

class Plazas (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE)
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    flg_conductor = models.BooleanField(default=False)
    estado = models.PositiveIntegerField(choices=estados_plazas, default=1)
    fechor_pendiente = models.DateTimeField(blank=True, null=True)
    fechor_confirmado = models.DateTimeField(blank=True, null=True)
    fechor_rechazado = models.DateTimeField(blank=True, null=True)
    fechor_cancelado = models.DateTimeField(blank=True, null=True)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'plazas'
        verbose_name_plural = 'plazas'

class Transferencias (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE)
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    tipo_transferencia = models.CharField(max_length=1, choices=tipo_transferencia, default='C')
    importe = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    tipo_descuento = models.CharField(max_length=2, choices=tipo_descuento, default='OP')
    importe_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    estado = models.PositiveIntegerField(choices=estado_transferencia, default=1)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'transferencias'
        verbose_name_plural = 'transferencias'

class MetodosPago (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id', on_delete=models.CASCADE)
    id_viaje = models.ForeignKey(Viajes, to_field='id', null=True, blank=True, on_delete=models.CASCADE)
    importe = models.DecimalField(max_digits = 5,decimal_places = 2, default=0.0)
    estado = models.PositiveIntegerField(choices=estado_transferencia, default=1)
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

class Localizaciones (models.Model):
    id_comunidadauto = models.PositiveIntegerField(default='-1')
    comunidadauto = models.CharField(max_length=3000, blank=True, null=True)
    id_provincia = models.PositiveIntegerField(default='-1')
    provincia = models.CharField(max_length=3000, blank=True, null=True)
    id_isla = models.PositiveIntegerField(default='-1')
    isla = models.CharField(max_length=3000, blank=True, null=True)
    dc = models.PositiveIntegerField(default='-1')
    id_municipio = models.PositiveIntegerField(default='-1')
    municipio = models.CharField(max_length=3000, blank=True, null=True)
    direccion = models.CharField(max_length=3000, blank=True, null=True)
    coordenada_x = models.DecimalField(max_digits = 32,decimal_places = 16, blank=True, null=True)
    coordenada_y = models.DecimalField(max_digits = 32, decimal_places = 16, blank=True, null=True)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'localizaciones'
        verbose_name_plural = 'localizaciones'

class Caparazones (models.Model):
    id_persona = models.ForeignKey(Personas,to_field='id',null=True,blank=True,on_delete=models.CASCADE)
    idiomas = models.CharField(max_length=128)
    profesion = models.CharField(max_length=64)
    aficiones = models.CharField(max_length=256)
    estilo_musica = models.CharField(max_length=64)
    grupos_musica = models.CharField(max_length=256)
    libros = models.CharField(max_length=256)
    peliculas = models.CharField(max_length=256)
    deportes = models.CharField(max_length=64)
    alimentacion = models.CharField(max_length=64)
    animales = models.CharField(max_length=64)
    fec_created = models.DateTimeField(auto_now_add=True)
    fec_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'caparazones'
        verbose_name_plural = 'caparazones'