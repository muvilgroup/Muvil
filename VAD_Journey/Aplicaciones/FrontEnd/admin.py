from django.contrib import admin
from .models import Personas, Vehiculos, Viajes, Reservas, Transferencias, Opiniones

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

class ReservasAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Reservas, ReservasAdmin)

class TransferenciasAdmin (admin.ModelAdmin):
    readonly_fields = ('fec_created', 'fec_updated')

admin.site.register(Transferencias, TransferenciasAdmin)

# Forma 2
@admin.register(Opiniones)
class OpinionesAdmin(admin.ModelAdmin):
    list_display = ('id','id_viaje','puntuacion','mensaje_opinion')
    readonly_fields = ('fec_created', 'fec_updated')

