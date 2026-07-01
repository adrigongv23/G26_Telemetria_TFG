from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum
from datetime import date

from temporadas.models import Temporada
from documentos.models import Factura
from users.decorators import require_rol
from .models import Gasto, Ingreso, Patrocinio
from .forms import GastoForm, IngresoForm, PatrocinioForm, PatrocinioEditForm

# Categorías válidas en Gasto (Documento usa 'normativa' en su lugar de 'general')
_CATEGORIAS_GASTO_VALIDAS = {c[0] for c in Gasto.CATEGORIAS_GASTOS}


@login_required
def inicio(request):
    temporada_activa = Temporada.objects.filter(actual=True).first()
    return render(request, 'index.html', {'temporada_actual': temporada_activa})


@require_rol('directiva')
def contabilidad(request):
    temporada_actual = Temporada.objects.filter(actual=True).first()

    gastos = []
    ingresos = []
    facturas_pendientes = []
    total_gastos = 0
    total_ingresos = 0
    presupuesto_inicial = 0
    presupuesto_actual = 0

    if temporada_actual:
        gastos = Gasto.objects.filter(temporada=temporada_actual)
        ingresos = Ingreso.objects.filter(temporada=temporada_actual)
        facturas_pendientes = Factura.objects.filter(
            temporada=temporada_actual, estado='pendiente'
        )

        total_gastos = gastos.aggregate(total=Sum('importe'))['total'] or 0
        total_ingresos = ingresos.aggregate(total=Sum('importe'))['total'] or 0
        presupuesto_inicial = temporada_actual.presupuesto
        presupuesto_actual = presupuesto_inicial - total_gastos + total_ingresos

    return render(request, 'contabilidad.html', {
        'temporada_actual': temporada_actual,
        'gastos': gastos,
        'ingresos': ingresos,
        'facturas_pendientes': facturas_pendientes,
        'total_gastos': total_gastos,
        'total_ingresos': total_ingresos,
        'presupuesto_inicial': presupuesto_inicial,
        'presupuesto_actual': presupuesto_actual,
        'gasto_form': GastoForm(),
        'ingreso_form': IngresoForm(),
    })


@require_rol('directiva')
@require_POST
def anadir_gasto(request):
    temporada_actual = Temporada.objects.filter(actual=True).first()
    if not temporada_actual:
        messages.error(request, 'No hay temporada activa.')
        return redirect('contabilidad')

    form = GastoForm(request.POST)
    if form.is_valid():
        gasto = form.save(commit=False)
        gasto.fecha = date.today()
        gasto.temporada = temporada_actual
        gasto.save()
        messages.success(request, 'Gasto añadido correctamente.')
    else:
        messages.error(request, 'Error al añadir el gasto. Revisa los datos.')
    return redirect('contabilidad')


@require_rol('directiva')
@require_POST
def anadir_ingreso(request):
    temporada_actual = Temporada.objects.filter(actual=True).first()
    if not temporada_actual:
        messages.error(request, 'No hay temporada activa.')
        return redirect('contabilidad')

    form = IngresoForm(request.POST)
    if form.is_valid():
        ingreso = form.save(commit=False)
        ingreso.fecha = date.today()
        ingreso.temporada = temporada_actual
        ingreso.save()
        messages.success(request, 'Ingreso añadido correctamente.')
    else:
        messages.error(request, 'Error al añadir el ingreso. Revisa los datos.')
    return redirect('contabilidad')


@require_rol('directiva')
@require_POST
def aceptar_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    temporada_actual = Temporada.objects.filter(actual=True).first()
    if not temporada_actual:
        messages.error(request, 'No hay temporada activa.')
        return redirect('contabilidad')

    categoria = factura.categoria if factura.categoria in _CATEGORIAS_GASTO_VALIDAS else 'general'
    Gasto.objects.create(
        concepto=factura.nombre,
        importe=factura.importe,
        fecha=date.today(),
        categoria=categoria,
        temporada=temporada_actual,
        observaciones=f'Factura de {factura.empresa}',
        doc_justificativo=factura.archivo,
    )
    factura.estado = 'aceptada'
    factura.save()
    messages.success(request, f'Factura de {factura.empresa} aceptada y registrada como gasto.')
    return redirect('contabilidad')


@require_rol('directiva')
@require_POST
def rechazar_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    factura.estado = 'rechazada'
    factura.save()
    messages.success(request, f'Factura de {factura.empresa} rechazada.')
    return redirect('contabilidad')


@login_required
def patrocinios(request):
    temporada_actual = Temporada.objects.filter(actual=True).first()
    pendientes = []
    aceptados = []
    denegados = []
    if temporada_actual:
        qs = Patrocinio.objects.filter(temporada=temporada_actual).select_related('contacto_equipo')
        pendientes = qs.filter(estado='en_contacto')
        aceptados = qs.filter(estado='aceptado')
        denegados = qs.filter(estado='denegado')
    return render(request, 'patrocinios.html', {
        'temporada_actual': temporada_actual,
        'pendientes': pendientes,
        'aceptados': aceptados,
        'denegados': denegados,
        'form': PatrocinioForm(),
    })


@login_required
@require_POST
def proponer_patrocinio(request):
    temporada_actual = Temporada.objects.filter(actual=True).first()
    if not temporada_actual:
        messages.error(request, 'No hay temporada activa. No se puede proponer un patrocinio.')
        return redirect('patrocinios')

    form = PatrocinioForm(request.POST)
    if form.is_valid():
        empresa = form.cleaned_data['empresa'].strip()
        if Patrocinio.objects.filter(empresa__iexact=empresa, temporada=temporada_actual).exists():
            messages.error(request, f'Ya existe un patrocinio con "{empresa}" en la temporada actual.')
        else:
            patrocinio = form.save(commit=False)
            patrocinio.estado = 'en_contacto'
            patrocinio.temporada = temporada_actual
            patrocinio.contacto_equipo = request.user
            patrocinio.save()
            messages.success(request, f'Patrocinio de "{empresa}" propuesto correctamente.')
    else:
        messages.error(request, 'Error en el formulario. Revisa los datos.')
    return redirect('patrocinios')


@require_rol('directiva')
def editar_patrocinio(request, pk):
    patrocinio = get_object_or_404(Patrocinio, pk=pk)
    form = PatrocinioEditForm(request.POST or None, instance=patrocinio)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Patrocinio actualizado correctamente.')
        return redirect('patrocinios')
    return render(request, 'editar_patrocinio.html', {'form': form, 'patrocinio': patrocinio})


@require_rol('directiva')
@require_POST
def cambiar_estado_patrocinio(request, pk):
    patrocinio = get_object_or_404(Patrocinio, pk=pk)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in ('aceptado', 'denegado', 'en_contacto'):
        patrocinio.estado = nuevo_estado
        patrocinio.save()
        messages.success(request, f'Estado de "{patrocinio.empresa}" actualizado.')
    return redirect('patrocinios')
