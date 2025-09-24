from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('ventas/', views.ventas, name='ventas'),
]
