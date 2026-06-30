from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.views.decorators.http import require_POST
from .decorators import require_rol
from .forms import PerfilForm, EditarUsuarioForm
from .models import CustomUser


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def mi_perfil(request):
    perfil_form = PerfilForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'guardar_perfil' in request.POST:
            perfil_form = PerfilForm(request.POST, instance=request.user)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Tus datos se han actualizado correctamente.')
                return redirect('mi_perfil')

        elif 'cambiar_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Tu contraseña se ha cambiado correctamente.')
                return redirect('mi_perfil')

    context = {
        'perfil_form': perfil_form,
        'password_form': password_form,
    }
    return render(request, 'mi_perfil.html', context)


@login_required
def listado_miembros(request):
    miembros = CustomUser.objects.all().order_by('last_name', 'first_name')

    rol = request.GET.get('rol', '')
    especialidad = request.GET.get('especialidad', '')
    apellido = request.GET.get('apellido', '')

    if rol:
        miembros = miembros.filter(rol=rol)
    if especialidad:
        miembros = miembros.filter(especialidad=especialidad)
    if apellido:
        miembros = miembros.filter(last_name__icontains=apellido)

    context = {
        'miembros': miembros,
        'rol_choices': CustomUser.ROL_CHOICES,
        'especialidad_choices': CustomUser.ESPECIALIDAD_CHOICES,
        'filtro_rol': rol,
        'filtro_especialidad': especialidad,
        'filtro_apellido': apellido,
    }
    return render(request, 'listado_miembros.html', context)


@require_rol('directiva')
def gestion_usuarios(request):
    usuarios = CustomUser.objects.all().order_by('last_name', 'first_name')

    rol = request.GET.get('rol', '')
    especialidad = request.GET.get('especialidad', '')
    apellido = request.GET.get('apellido', '')

    if rol:
        usuarios = usuarios.filter(rol=rol)
    if especialidad:
        usuarios = usuarios.filter(especialidad=especialidad)
    if apellido:
        usuarios = usuarios.filter(last_name__icontains=apellido)

    context = {
        'usuarios': usuarios,
        'rol_choices': CustomUser.ROL_CHOICES,
        'especialidad_choices': CustomUser.ESPECIALIDAD_CHOICES,
        'filtro_rol': rol,
        'filtro_especialidad': especialidad,
        'filtro_apellido': apellido,
    }
    return render(request, 'gestion_usuarios.html', context)


@require_rol('directiva')
def editar_usuario(request, pk):
    usuario = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'El usuario se ha actualizado correctamente.')
            return redirect('gestion_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'editar_usuario.html', {'form': form, 'usuario': usuario})


@require_rol('directiva')
@require_POST
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(CustomUser, pk=pk)
    usuario.delete()
    messages.success(request, 'El usuario se ha eliminado correctamente.')
    return redirect('gestion_usuarios')
