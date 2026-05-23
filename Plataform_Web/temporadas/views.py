from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from temporadas.models import Temporada  # Importamos tu modelo Temporada

@login_required
def dashboard(request):
    # Buscamos en la base de datos la temporada que tenga actual=True.
    # Usamos .first() por seguridad para evitar errores si no hubiera ninguna creada todavía.
    temporada_activa = Temporada.objects.filter(actual=True).first()
    
    # Metemos los datos en el diccionario de contexto para mandarlos al HTML
    context = {
        'temporada_actual': temporada_activa
    }
    
    return render(request, 'index.html', context)