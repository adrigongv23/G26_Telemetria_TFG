from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from users.decorators import require_rol
from temporadas.models import Temporada
from .models import Prueba, Telemetria, Variable
from .forms import PruebaForm, TelemetriaForm
from .telemetry_parser import procesar_csv, canales_para_variables, TelemetriaCSVError


def puede_subir_csv(user):
    return user.rol == 'directiva' or user.especialidad == 'software'


@login_required
@require_GET
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
@require_GET
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

        try:
            canales = canales_para_variables(telemetria.archivo_csv.path)
            Variable.objects.bulk_create([
                Variable(telemetria=telemetria, nombre=label, unidad_medida=unidad, descripcion=f'Columna CSV: {columna}')
                for columna, label, unidad in canales
            ])
        except Exception:
            pass

        messages.success(request, 'Archivo de telemetría subido correctamente.')
    else:
        messages.error(request, 'No se pudo subir el archivo. Revisa el formulario.')
    return redirect('detalle_prueba', pk=prueba.pk)


@login_required
@require_GET
def ver_csv(request, pk):
    telemetria = get_object_or_404(Telemetria, pk=pk)

    try:
        datos = procesar_csv(telemetria.archivo_csv.path)
    except TelemetriaCSVError as exc:
        messages.error(request, f'No se ha podido procesar el CSV: {exc}')
        return redirect('detalle_prueba', pk=telemetria.prueba_id)
    except (FileNotFoundError, OSError):
        messages.error(request, 'El archivo CSV ya no existe en el servidor.')
        return redirect('detalle_prueba', pk=telemetria.prueba_id)
    except Exception:
        messages.error(request, 'Ha ocurrido un error inesperado al procesar el CSV.')
        return redirect('detalle_prueba', pk=telemetria.prueba_id)

    return render(request, 'ver_csv.html', {
        'telemetria': telemetria,
        'prueba': telemetria.prueba,
        'datos': datos,
    })


@login_required
@require_POST
def eliminar_telemetria(request, pk):
    telemetria = get_object_or_404(Telemetria, pk=pk)
    if not puede_subir_csv(request.user):
        messages.error(request, 'No tienes permiso para eliminar archivos de telemetría.')
        return redirect('detalle_prueba', pk=telemetria.prueba_id)

    prueba_pk = telemetria.prueba_id
    nombre = telemetria.nombre
    telemetria.delete()
    messages.success(request, f'"{nombre}" eliminado correctamente.')
    return redirect('detalle_prueba', pk=prueba_pk)
