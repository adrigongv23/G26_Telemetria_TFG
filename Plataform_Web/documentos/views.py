from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import Http404

from temporadas.models import Temporada
from users.areas import get_area_nombre, get_area_color, es_miembro_area, es_gestor_area
from .models import Documento
from .forms import DocumentoForm, DocumentoEditForm


@login_required
def documentos_area(request, especialidad):
    area_nombre = get_area_nombre(especialidad)
    if area_nombre is None:
        raise Http404('Área técnica no reconocida.')

    documentos = Documento.objects.filter(categoria=especialidad).select_related('subido_por')

    context = {
        'especialidad': especialidad,
        'area_nombre': area_nombre,
        'area_color': get_area_color(especialidad),
        'documentos': documentos,
        'puede_anadir': es_miembro_area(request.user, especialidad),
        'puede_gestionar': es_gestor_area(request.user, especialidad),
        'form': DocumentoForm(),
    }
    return render(request, 'documentos_area.html', context)


@login_required
@require_POST
def anadir_documento(request, especialidad):
    if get_area_nombre(especialidad) is None:
        raise Http404('Área técnica no reconocida.')
    if not es_miembro_area(request.user, especialidad):
        raise PermissionDenied('No perteneces a esta área técnica.')

    form = DocumentoForm(request.POST, request.FILES)
    if form.is_valid():
        documento = form.save(commit=False)
        documento.categoria = especialidad
        documento.subido_por = request.user
        documento.save()

        temporada_actual = Temporada.objects.filter(actual=True).first()
        if temporada_actual:
            documento.temporada.add(temporada_actual)

        messages.success(request, 'Documento añadido correctamente.')
    else:
        messages.error(request, 'Error al añadir el documento. Revisa los datos.')

    return redirect('documentos_area', especialidad=especialidad)


@login_required
def editar_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    if not es_gestor_area(request.user, documento.categoria):
        raise PermissionDenied('Solo el Jefe de Área puede editar este documento.')

    if request.method == 'POST':
        form = DocumentoEditForm(request.POST, instance=documento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento actualizado correctamente.')
            return redirect('documentos_area', especialidad=documento.categoria)
    else:
        form = DocumentoEditForm(instance=documento)

    return render(request, 'editar_documento.html', {'form': form, 'documento': documento})


@login_required
@require_POST
def eliminar_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    if not es_gestor_area(request.user, documento.categoria):
        raise PermissionDenied('Solo el Jefe de Área puede eliminar este documento.')

    especialidad = documento.categoria
    documento.delete()
    messages.success(request, 'Documento eliminado correctamente.')
    return redirect('documentos_area', especialidad=especialidad)
