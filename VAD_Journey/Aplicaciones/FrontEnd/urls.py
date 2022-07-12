from django.urls import path
from Aplicaciones.FrontEnd.views import v_home

urlpatterns = [
    path('', v_home),
]