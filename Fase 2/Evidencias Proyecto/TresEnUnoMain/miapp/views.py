from django.shortcuts import render
from django.db.models import Prefetch
from .models import Producto, Categoria, Oferta
from django.utils import timezone 

def inicio(request):
    ofertas_activas = Oferta.objects.filter(fecha_fin__gte=timezone.now(), fecha_inicio__lte=timezone.now())
    
    productos_destacados = Producto.objects.filter(id_categoria__nombre_categoria='Hortalizas').prefetch_related(
        Prefetch('oferta_set', queryset=ofertas_activas, to_attr='ofertas_activas')
    ).order_by('?')[:3]

    contexto = {
        'productos': productos_destacados,
        'now': timezone.now(), 
    }
    return render(request, 'miapp/inicio.html', contexto)

def nosotros(request):
    return render(request, 'miapp/nosotros.html')

def listar_productos(request):
    ofertas_activas = Oferta.objects.filter(fecha_fin__gte=timezone.now(), fecha_inicio__lte=timezone.now())
    
    productos = Producto.objects.all().prefetch_related(
        Prefetch('oferta_set', queryset=ofertas_activas, to_attr='ofertas_activas')
    )
    
    contexto = {
        'productos': productos,
        'now': timezone.now(), 
    }
    return render(request, 'miapp/productos.html', contexto)

def ventas(request):
    return render(request, 'miapp/ventas.html')