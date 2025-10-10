from django.urls import path
from .views import (
    ClienteRegistroAPIView, 
    ClienteLoginAPIView, 
    VerifyTokenAPIView,
    ClienteDetailAPIView,
    ProductoListAPIView,
    ProductoDetailAPIView,
    CarritoView,              # NUEVO
    CarritoItemView,          # NUEVO
    CarritoVaciarView         # NUEVO
)
from . import views

urlpatterns = [
    # ===== RUTAS DE PÁGINAS HTML =====
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),  # NUEVO
    path('contacto/', views.ventas, name='contacto'),
    path('perfil/', views.perfil_temporal, name='perfil'),
    
    # ===== RUTAS DE AUTENTICACIÓN =====
    path('auth/register', views.cliente_registro_form, name='registro-form'),
    path('auth/login', views.cliente_login_form, name='login-form'),
    
    # ===== API ENDPOINTS - AUTENTICACIÓN =====
    path('api/auth/register', ClienteRegistroAPIView.as_view(), name='cliente-registro'),
    path('api/auth/login', ClienteLoginAPIView.as_view(), name='cliente-login'),
    path('api/auth/verify-token', VerifyTokenAPIView.as_view(), name='verify-token'),
    path('api/clientes/me', ClienteDetailAPIView.as_view(), name='cliente-detail'),
    
    # ===== API ENDPOINTS - PRODUCTOS (PÚBLICOS) =====
    path('api/public/products/', ProductoListAPIView.as_view(), name='productos-list'),
    path('api/public/products/<int:pk>/', ProductoDetailAPIView.as_view(), name='producto-detail'),
    
    # ===== API ENDPOINTS - CARRITO (NUEVOS) =====
    path('api/cart/', CarritoView.as_view(), name='carrito'),
    path('api/cart/<int:producto_id>/', CarritoItemView.as_view(), name='carrito-item'),
    path('api/cart/clear/', CarritoVaciarView.as_view(), name='carrito-vaciar'),
]