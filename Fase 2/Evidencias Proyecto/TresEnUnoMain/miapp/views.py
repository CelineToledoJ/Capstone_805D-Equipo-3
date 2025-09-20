
from django.shortcuts import render, redirect

def inicio(request):
    return render(request, 'miapp/inicio.html')

def nosotros(request):
    return render(request, 'miapp/nosotros.html')

def productos(request):
    return render(request, 'miapp/productos.html')

def ventas(request):
    return render(request, 'miapp/ventas.html')