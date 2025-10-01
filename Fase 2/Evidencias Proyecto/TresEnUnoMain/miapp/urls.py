from django.urls import path
from .views import (
    ClienteRegistroAPIView, 
    ClienteLoginAPIView, 
    VerifyTokenAPIView,
    ClienteDetailAPIView
)
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('productos/', views.listar_productos, name='listar_productos'),
    
    path('contacto/', views.ventas, name='contacto'),
    
    path('perfil/', views.perfil_temporal, name='perfil'),
    
    path('api/auth/register', views.ClienteRegistroAPIView.as_view(), name='cliente-registro'),
    path('api/auth/login', views.ClienteLoginAPIView.as_view(), name='cliente-login'),
    path('api/auth/verify-token', VerifyTokenAPIView.as_view(), name='verify-token'),
    
    path('api/clientes/me', ClienteDetailAPIView.as_view(), name='cliente-detail'), 
    
    path('auth/register', views.cliente_registro_form, name='registro-form'),
    
    # La plantilla barrabase.html hace referencia a 'login-form'
    path('auth/login', views.cliente_login_form, name='login-form'), 
]