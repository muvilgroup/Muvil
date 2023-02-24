from django.contrib import admin
from .models import Personas, Vehiculos, Viajes, Reservas, Transferencias, Opiniones

# Register your models here.

# Forma 1
admin.site.register(Personas)
admin.site.register(Vehiculos)
admin.site.register(Viajes)
admin.site.register(Reservas)
admin.site.register(Transferencias)

# Forma 2
@admin.register(Opiniones)
class OpinionesAdmin(admin.ModelAdmin):
    list_display = ('id','id_viaje','puntuacion','mensaje_opinion')

