from django.contrib import admin
from .models import Personas, Vehiculos, Viajes, Plazas, Transferencias, Opiniones, Mensajes

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

admin.site.register(Plazas, PlazasAdmin)

class TransferenciasAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Transferencias, TransferenciasAdmin)

class MensajesAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Mensajes, MensajesAdmin)

# Forma 2
@admin.register(Opiniones)
class OpinionesAdmin(admin.ModelAdmin):
    list_display = ('id','id_viaje','puntuacion','mensaje_opinion')
    readonly_fields = ('fec_created', 'fec_updated')

