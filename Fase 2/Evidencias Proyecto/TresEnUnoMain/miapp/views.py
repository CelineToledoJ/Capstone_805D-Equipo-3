from django.shortcuts import render
from .models import Producto, Categoria 

def inicio(request):
    
    productos_destacados = Producto.objects.all().order_by('id')[:3]
    contexto = {
        'productos_destacados': productos_destacados, 
    }
    return render(request, 'miapp/inicio.html', contexto)

def nosotros(request):
    return render(request, 'miapp/nosotros.html')

def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'miapp/productos.html', {'productos': productos})

def ventas(request):
    return render(request, 'miapp/ventas.html')