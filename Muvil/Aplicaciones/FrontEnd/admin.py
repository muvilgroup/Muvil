from django.contrib import admin
from .models import Personas, Vehiculos, Viajes, Plazas, Transferencias, Opiniones, Mensajes, Localizaciones, \
                    Caparazones

# Register your models here.

# Forma 1
class PersonasAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Personas, PersonasAdmin)

class VehiculosAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Vehiculos, VehiculosAdmin)

class ViajesAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Viajes, ViajesAdmin)

class PlazasAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')
    list_display = ('id', 'id_viaje','id_persona','flg_conductor')

admin.site.register(Plazas, PlazasAdmin)

class TransferenciasAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Transferencias, TransferenciasAdmin)

class MensajesAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Mensajes, MensajesAdmin)

class LocalizacionesAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Localizaciones, LocalizacionesAdmin)

class CaparazonesAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Caparazones, CaparazonesAdmin)

# Forma 2
@admin.register(Opiniones)
class OpinionesAdmin(admin.ModelAdmin):
    list_display = ('id','id_viaje','puntuacion','mensaje_opinion')
    readonly_fields = ('fec_created', 'fec_updated')

