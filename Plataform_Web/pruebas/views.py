from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from users.decorators import require_rol
from temporadas.models import Temporada
from .models import Prueba
from .forms import PruebaForm, TelemetriaForm


def puede_subir_csv(user):
    return user.rol == 'directiva' or user.especialidad == 'software'


@login_required
def listado_pruebas(request):
    temporada_actual = Temporada.objects.filter(actual=True).first()
    temporada_id = request.GET.get('temporada') or (temporada_actual.pk if temporada_actual else None)
    categoria = request.GET.get('categoria')

    pruebas = Prueba.objects.all()
    if temporada_id:
        pruebas = pruebas.filter(temporada_id=temporada_id)
    if categoria:
        pruebas = pruebas.filter(categoria=categoria)

    return render(request, 'listado_pruebas.html', {
        'pruebas': pruebas,
        'temporadas': Temporada.objects.all(),
        'categorias': Prueba.CATEGORIAS_TEST,
        'temporada_seleccionada': str(temporada_id) if temporada_id else '',
        'categoria_seleccionada': categoria or '',
    })


@login_required
def detalle_prueba(request, pk):
    prueba = get_object_or_404(Prueba, pk=pk)
    puede_editar = request.user.rol == 'directiva' or (
        request.user.rol == 'jefe_area' and prueba.realizado_por_id == request.user.id
    )
    return render(request, 'detalle_prueba.html', {
        'prueba': prueba,
        'puede_editar': puede_editar,
        'puede_subir_csv': puede_subir_csv(request.user),
        'form_csv': TelemetriaForm(),
    })


@require_rol('directiva', 'jefe_area')
def crear_prueba(request):
    form = PruebaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        prueba = form.save(commit=False)
        prueba.realizado_por = request.user
        prueba.save()
        messages.success(request, 'Test creado correctamente.')
        return redirect('listado_pruebas')
    return render(request, 'editar_prueba.html', {'form': form, 'prueba': None})


@require_rol('directiva', 'jefe_area')
def editar_prueba(request, pk):
    prueba = get_object_or_404(Prueba, pk=pk)
    if request.user.rol == 'jefe_area' and prueba.realizado_por_id != request.user.id:
        messages.error(request, 'Solo puedes editar los tests que tú has creado.')
        return redirect('detalle_prueba', pk=prueba.pk)

    form = PruebaForm(request.POST or None, instance=prueba)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Test actualizado correctamente.')
        return redirect('detalle_prueba', pk=prueba.pk)
    return render(request, 'editar_prueba.html', {'form': form, 'prueba': prueba})


@require_rol('directiva')
@require_POST
def eliminar_prueba(request, pk):
    prueba = get_object_or_404(Prueba, pk=pk)
    prueba.delete()
    messages.success(request, f'Test "{prueba.nombre}" eliminado.')
    return redirect('listado_pruebas')


@login_required
@require_POST
def subir_csv(request, pk):
    prueba = get_object_or_404(Prueba, pk=pk)
    if not puede_subir_csv(request.user):
        messages.error(request, 'No tienes permiso para subir archivos de telemetría.')
        return redirect('detalle_prueba', pk=prueba.pk)

    form = TelemetriaForm(request.POST, request.FILES)
    if form.is_valid():
        telemetria = form.save(commit=False)
        telemetria.prueba = prueba
        telemetria.save()
        messages.success(request, 'Archivo de telemetría subido correctamente.')
    else:
        messages.error(request, 'No se pudo subir el archivo. Revisa el formulario.')
    return redirect('detalle_prueba', pk=prueba.pk)
