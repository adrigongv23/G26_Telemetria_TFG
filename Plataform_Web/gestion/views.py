from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    # Esta función es la que decide qué mostrar cuando alguien entra a la web
    return HttpResponse("<h1>¡Bienvenido a la Plataforma de Gades! 🏎️💨</h1><p>Sistema de Telemetría y Gestión v1.0</p>")