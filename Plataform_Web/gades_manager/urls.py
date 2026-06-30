"""
URL configuration for gades_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from gestion import views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('mi-perfil/', users_views.mi_perfil, name='mi_perfil'),
    path('miembros/', users_views.listado_miembros, name='listado_miembros'),
    path('gestion/usuarios/', users_views.gestion_usuarios, name='gestion_usuarios'),
    path('gestion/usuarios/<int:pk>/editar/', users_views.editar_usuario, name='editar_usuario'),
    path('gestion/usuarios/<int:pk>/eliminar/', users_views.eliminar_usuario, name='eliminar_usuario'),
]