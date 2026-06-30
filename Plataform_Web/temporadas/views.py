from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from users.decorators import require_rol
from .models import Temporada
from .forms import TemporadaForm


@require_rol('directiva')
def gestion_temporadas(request):
    temporadas = Temporada.objects.all()
    return render(request, 'gestion_temporadas.html', {'temporadas': temporadas})


@require_rol('directiva')
def crear_temporada(request):
    form = TemporadaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Temporada creada correctamente.')
        return redirect('gestion_temporadas')
    return render(request, 'editar_temporada.html', {'form': form, 'temporada': None})


@require_rol('directiva')
def editar_temporada(request, pk):
    temporada = get_object_or_404(Temporada, pk=pk)
    form = TemporadaForm(request.POST or None, instance=temporada)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Temporada actualizada correctamente.')
        return redirect('gestion_temporadas')
    return render(request, 'editar_temporada.html', {'form': form, 'temporada': temporada})


@require_rol('directiva')
@require_POST
def eliminar_temporada(request, pk):
    temporada = get_object_or_404(Temporada, pk=pk)
    temporada.delete()
    messages.success(request, f'Temporada "{temporada.nombre}" eliminada.')
    return redirect('gestion_temporadas')
