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
from temporadas import views as temporadas_views

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
    path('gestion/temporadas/', temporadas_views.gestion_temporadas, name='gestion_temporadas'),
    path('gestion/temporadas/crear/', temporadas_views.crear_temporada, name='crear_temporada'),
    path('gestion/temporadas/<int:pk>/editar/', temporadas_views.editar_temporada, name='editar_temporada'),
    path('gestion/temporadas/<int:pk>/eliminar/', temporadas_views.eliminar_temporada, name='eliminar_temporada'),
    path('gestion/contabilidad/', views.contabilidad, name='contabilidad'),
    path('gestion/contabilidad/gasto/anadir/', views.anadir_gasto, name='anadir_gasto'),
    path('gestion/contabilidad/ingreso/anadir/', views.anadir_ingreso, name='anadir_ingreso'),
    path('gestion/contabilidad/factura/<int:pk>/aceptar/', views.aceptar_factura, name='aceptar_factura'),
    path('gestion/contabilidad/factura/<int:pk>/rechazar/', views.rechazar_factura, name='rechazar_factura'),
    path('patrocinios/', views.patrocinios, name='patrocinios'),
    path('patrocinios/proponer/', views.proponer_patrocinio, name='proponer_patrocinio'),
    path('patrocinios/<int:pk>/editar/', views.editar_patrocinio, name='editar_patrocinio'),
    path('patrocinios/<int:pk>/estado/', views.cambiar_estado_patrocinio, name='cambiar_estado_patrocinio'),
]