from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum
from datetime import date

from django.http import Http404

from temporadas.models import Temporada
from documentos.models import Factura
from users.decorators import require_rol
from users.models import CustomUser
from .models import Gasto, Ingreso, Patrocinio
from .forms import GastoForm, IngresoForm, PatrocinioForm, PatrocinioEditForm

# Categorías válidas en Gasto (Documento usa 'normativa' en su lugar de 'general')
_CATEGORIAS_GASTO_VALIDAS = {c[0] for c in Gasto.CATEGORIAS_GASTOS}

# Color de acento por área técnica, reutilizando la paleta ya cargada de Bootstrap
AREA_COLORS = {
    'aerodinamica': '#0dcaf0',
    'chasis': '#6c757d',
    'business_operations': '#fd7e14',
    'epowertrain': '#198754',
    'electronica': '#6610f2',
    'sdf': '#6f42c1',
    'motor_transmision': '#dc3545',
    'software': '#20c997',
}

# Icono (trazo SVG, viewBox 24x24) por área técnica. Las áreas sin entrada
# aquí usan el hexágono genérico como icono por defecto.
AREA_ICONS = {
    'software': 'M8 9l-4 3 4 3M16 9l4 3-4 3M14 6l-4 12',
}
AREA_ICON_DEFAULT = 'M12 2l8 4.5v9L12 20l-8-4.5v-9L12 2z'


def _darken(hex_color, factor=0.55):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c * factor) for c in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'


@login_required
def inicio(request):
    temporada_activa = Temporada.objects.filter(actual=True).first()
    return render(request, 'index.html', {'temporada_actual': temporada_activa})


@login_required
def area_tecnica(request, especialidad):
    area_nombre = dict(CustomUser.ESPECIALIDAD_CHOICES).get(especialidad)
    if area_nombre is None:
        raise Http404('Área técnica no reconocida.')

    # Preferimos un Jefe de Área; si aún no hay ninguno asignado en esa
    # especialidad, mostramos a un miembro de directiva de esa misma área.
    responsable = CustomUser.objects.filter(especialidad=especialidad, rol='jefe_area').first()
    if not responsable:
        responsable = CustomUser.objects.filter(especialidad=especialidad, rol='directiva').first()

    if responsable:
        responsable_nombre = f'{responsable.first_name} {responsable.last_name}'.strip() or responsable.username
        responsable_iniciales = (responsable.first_name[:1] + responsable.last_name[:1]).upper() or '?'
    else:
        responsable_nombre = 'Sin asignar'
        responsable_iniciales = '?'

    area_color = AREA_COLORS.get(especialidad, '#0d6efd')

    return render(request, 'area_tecnica.html', {
        'especialidad': especialidad,
        'area_nombre': area_nombre,
        'area_color': area_color,
        'area_color_dark': _darken(area_color),
        'area_icon_path': AREA_ICONS.get(especialidad, AREA_ICON_DEFAULT),
        'responsable_nombre': responsable_nombre,
        'responsable_iniciales': responsable_iniciales,
    })


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
