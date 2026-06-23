from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import PerfilForm


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
