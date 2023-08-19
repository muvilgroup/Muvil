from django.shortcuts import redirect
from django.contrib import messages
from .models import Personas, Vehiculos

def check_logued_usuario (function=None, redirect_url='n_pagina_principal'):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary by default.
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):

            ###### BEGIN decorator body
            if not request.user.is_authenticated:
                messages.error(request, "¡¡¡Debes iniciar sesión para navegar en MUVIL!!!.")
                return redirect(redirect_url)
            ###### END decorator body

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator

def get_persona_usuario (function=None):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary by default.
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):

            ###### BEGIN decorator body
            usuario = Personas.objects.get(id_usuario=request.user.id)

            kwargs['usuario'] = usuario
            ###### END decorator body

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator

def get_vehiculos_usuario(function=None):
    """
    Decorador para obtener los vehiculos del usuario
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            ###### BEGIN decorator body
            usuario = Personas.objects.get(id_usuario=request.user.id)
            vehiculos = Vehiculos.objects.all().filter(id_persona=usuario)

            kwargs['vehiculos'] = vehiculos
            ###### END decorator body

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator
