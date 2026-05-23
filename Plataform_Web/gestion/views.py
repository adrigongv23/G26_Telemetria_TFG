from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from temporadas.models import Temporada

@login_required
def inicio(request):
    # Buscamos la temporada que configuraste como actual
    temporada_activa = Temporada.objects.filter(actual=True).first()
    
    context = {
        'temporada_actual': temporada_activa
    }
    # Renderiza index.html, el cual hereda automáticamente de base.html
    return render(request, 'index.html', context)