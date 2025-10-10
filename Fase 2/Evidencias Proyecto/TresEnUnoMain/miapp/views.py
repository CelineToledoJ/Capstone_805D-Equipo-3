from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Producto, Categoria, Oferta, Cliente
from django.utils import timezone 

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated 

from rest_framework_simplejwt.tokens import RefreshToken 

from .serializers import (
    ClienteRegistroSerializer,
    ClienteLoginSerializer,
    ClienteSerializer,
    ProductoSerializer,
    ProductoListSerializer
)

# ===== VISTAS HTML =====

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

def detalle_producto(request, producto_id):
    """
    Vista que renderiza la página HTML del detalle del producto
    URL: /producto/<id>
    """
    # Verificamos que el producto exista
    producto = get_object_or_404(Producto, pk=producto_id)
    
    # Obtenemos ofertas activas del producto
    ofertas_activas = Oferta.objects.filter(
        id_producto=producto,
        fecha_fin__gte=timezone.now(),
        fecha_inicio__lte=timezone.now()
    )
    
    contexto = {
        'producto': producto,
        'ofertas': ofertas_activas,
        'now': timezone.now(),
    }
    
    return render(request, 'miapp/detalle_producto.html', contexto)

def ventas(request):
    return render(request, 'miapp/ventas.html')

def cliente_registro_form(request):
    """Renderiza el formulario simple de registro."""
    return render(request, 'miapp/registro.html')

def cliente_login_form(request):
    """Renderiza el formulario simple de login."""
    return render(request, 'miapp/login.html')

def perfil_temporal(request):
    """Renderiza una vista simple para el enlace 'Mi Perfil' de la barra de navegación."""
    return render(request, 'miapp/perfil.html') 

# ===== API VIEWS - AUTENTICACIÓN =====

class ClienteRegistroAPIView(generics.CreateAPIView):
    """
    Endpoint POST /api/auth/register
    Permite el registro de un nuevo cliente.
    """
    serializer_class = ClienteRegistroSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            cliente = serializer.save()
            
            return Response({
                "message": "Registro de cliente exitoso.",
                "cliente_id": cliente.id,
                "correo": cliente.correo
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_tokens_for_user(cliente):
    refresh = RefreshToken.for_user(cliente) 
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class ClienteLoginAPIView(generics.GenericAPIView):
    """
    Endpoint POST /api/auth/login
    Procesa el login, valida las credenciales y devuelve tokens JWT.
    """
    serializer_class = ClienteLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            
            cliente = serializer.validated_data['cliente']
            
            tokens = get_tokens_for_user(cliente)
            
            return Response({
                "message": "Login exitoso.",
                "tokens": tokens,
                "cliente_id": cliente.id,
                "correo": cliente.correo
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyTokenAPIView(APIView):
    """
    Endpoint GET /api/auth/verify-token
    Ruta protegida simple para verificar si el token JWT es válido y el usuario existe.
    """
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        return Response({
            "message": "Token válido y usuario activo.",
            "cliente_id": request.user.id
        }, status=status.HTTP_200_OK)

class ClienteDetailAPIView(generics.RetrieveAPIView):
    """
    Endpoint GET /api/clientes/me
    Devuelve los detalles del cliente actualmente autenticado (solicitud.user).
    """
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# ===== API VIEWS - PRODUCTOS =====

class ProductoListAPIView(generics.ListAPIView):
    """
    Endpoint GET /api/public/products
    Lista todos los productos disponibles (público)
    """
    queryset = Producto.objects.all().select_related('imagen', 'id_categoria')
    serializer_class = ProductoListSerializer
    
    def get_queryset(self):
        """
        Opcionalmente permite filtrar por categoría
        Ejemplo: /api/public/products?categoria=Hortalizas
        """
        queryset = super().get_queryset()
        categoria = self.request.query_params.get('categoria', None)
        
        if categoria:
            queryset = queryset.filter(id_categoria__nombre_categoria__icontains=categoria)
        
        return queryset


class ProductoDetailAPIView(generics.RetrieveAPIView):
    """
    Endpoint GET /api/public/products/:id
    Obtiene el detalle completo de un producto específico (público)
    """
    queryset = Producto.objects.all().select_related('imagen', 'id_categoria').prefetch_related('oferta_set')
    serializer_class = ProductoSerializer
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        """
        Sobrescribe el método retrieve para manejar productos no encontrados
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Producto.DoesNotExist:
            return Response(
                {"error": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )