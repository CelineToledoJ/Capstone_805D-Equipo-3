from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Producto, Categoria, Oferta, Cliente
from django.utils import timezone 

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated 

from rest_framework_simplejwt.tokens import RefreshToken 
from decimal import Decimal

from .serializers import (
    ClienteRegistroSerializer,
    ClienteLoginSerializer,
    ClienteSerializer,
    ProductoSerializer,
    ProductoListSerializer,
    CarritoItemSerializer,
    CarritoSerializer
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

# AGREGAR ESTOS IMPORTS AL INICIO DEL ARCHIVO (si no los tienes):

def obtener_carrito(request):
    """
    Obtiene el carrito de la sesión.
    Estructura: {'items': {producto_id: cantidad, ...}}
    """
    carrito = request.session.get('carrito', {'items': {}})
    return carrito


def guardar_carrito(request, carrito):
    """Guarda el carrito en la sesión"""
    request.session['carrito'] = carrito
    request.session.modified = True


def calcular_carrito_completo(carrito):
    """
    Calcula el carrito completo con información de productos y totales.
    Retorna un diccionario con items detallados, total y cantidad de items.
    """
    items_detallados = []
    total = Decimal('0.00')
    
    for producto_id_str, cantidad in carrito.get('items', {}).items():
        try:
            producto_id = int(producto_id_str)
            producto = Producto.objects.select_related('imagen', 'id_categoria').get(pk=producto_id)
            
            # Calcular precio (con oferta si existe)
            now = timezone.now()
            oferta = producto.oferta_set.filter(
                fecha_inicio__lte=now,
                fecha_fin__gte=now
            ).first()
            
            precio = Decimal(str(oferta.precio_oferta)) if oferta else Decimal(str(producto.precio_unitario))
            subtotal = precio * cantidad
            
            # Obtener URL de imagen
            imagen_url = None
            if producto.imagen and producto.imagen.imagen:
                imagen_url = producto.imagen.imagen.url
            
            item = {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio_unitario': precio,
                'cantidad': cantidad,
                'unidad_medida': producto.unidad_medida,
                'imagen_url': imagen_url,
                'stock_disponible': producto.stock_disponible,
                'subtotal': subtotal
            }
            
            items_detallados.append(item)
            total += subtotal
            
        except (Producto.DoesNotExist, ValueError):
            # Si el producto ya no existe, lo omitimos
            continue
    
    return {
        'items': items_detallados,
        'total': total,
        'cantidad_items': sum(item['cantidad'] for item in items_detallados)
    }


# ===== API VIEWS PARA EL CARRITO =====

class CarritoView(APIView):
    """
    GET /api/cart - Obtener el carrito actual
    POST /api/cart - Agregar un producto al carrito
    """
    
    def get(self, request):
        """Obtiene el contenido del carrito"""
        carrito = obtener_carrito(request)
        carrito_completo = calcular_carrito_completo(carrito)
        
        serializer = CarritoSerializer(carrito_completo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Agrega un producto al carrito"""
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad', 1)
        
        # Validar datos
        item_serializer = CarritoItemSerializer(data={
            'producto_id': producto_id,
            'cantidad': cantidad
        })
        
        if not item_serializer.is_valid():
            return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener carrito actual
        carrito = obtener_carrito(request)
        
        # Agregar o actualizar cantidad
        producto_id_str = str(producto_id)
        cantidad_actual = carrito['items'].get(producto_id_str, 0)
        nueva_cantidad = cantidad_actual + cantidad
        
        # Verificar stock
        try:
            producto = Producto.objects.get(pk=producto_id)
            if nueva_cantidad > producto.stock_disponible:
                return Response({
                    'error': f'Stock insuficiente. Solo hay {producto.stock_disponible} unidades disponibles.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            carrito['items'][producto_id_str] = nueva_cantidad
            guardar_carrito(request, carrito)
            
            # Retornar carrito actualizado
            carrito_completo = calcular_carrito_completo(carrito)
            serializer = CarritoSerializer(carrito_completo)
            
            return Response({
                'message': f'{producto.nombre} agregado al carrito',
                'carrito': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class CarritoItemView(APIView):
    """
    PUT /api/cart/<producto_id> - Actualizar cantidad de un producto
    DELETE /api/cart/<producto_id> - Eliminar un producto del carrito
    """
    
    def put(self, request, producto_id):
        """Actualiza la cantidad de un producto en el carrito"""
        nueva_cantidad = request.data.get('cantidad')
        
        if not nueva_cantidad or nueva_cantidad < 1:
            return Response({'error': 'Cantidad inválida'}, status=status.HTTP_400_BAD_REQUEST)
        
        carrito = obtener_carrito(request)
        producto_id_str = str(producto_id)
        
        if producto_id_str not in carrito['items']:
            return Response({'error': 'Producto no está en el carrito'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar stock
        try:
            producto = Producto.objects.get(pk=producto_id)
            if nueva_cantidad > producto.stock_disponible:
                return Response({
                    'error': f'Stock insuficiente. Solo hay {producto.stock_disponible} unidades disponibles.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            carrito['items'][producto_id_str] = nueva_cantidad
            guardar_carrito(request, carrito)
            
            carrito_completo = calcular_carrito_completo(carrito)
            serializer = CarritoSerializer(carrito_completo)
            
            return Response({
                'message': 'Cantidad actualizada',
                'carrito': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, producto_id):
        """Elimina un producto del carrito"""
        carrito = obtener_carrito(request)
        producto_id_str = str(producto_id)
        
        if producto_id_str in carrito['items']:
            del carrito['items'][producto_id_str]
            guardar_carrito(request, carrito)
            
            carrito_completo = calcular_carrito_completo(carrito)
            serializer = CarritoSerializer(carrito_completo)
            
            return Response({
                'message': 'Producto eliminado del carrito',
                'carrito': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Producto no está en el carrito'}, status=status.HTTP_404_NOT_FOUND)


class CarritoVaciarView(APIView):
    """DELETE /api/cart/clear - Vaciar todo el carrito"""
    
    def delete(self, request):
        """Vacía completamente el carrito"""
        request.session['carrito'] = {'items': {}}
        request.session.modified = True
        
        return Response({
            'message': 'Carrito vaciado',
            'carrito': {
                'items': [],
                'total': 0,
                'cantidad_items': 0
            }
        }, status=status.HTTP_200_OK)


# ===== VISTA HTML PARA LA PÁGINA DEL CARRITO =====

def ver_carrito(request):
    """
    Vista que renderiza la página HTML del carrito
    URL: /carrito/
    """
    carrito = obtener_carrito(request)
    carrito_completo = calcular_carrito_completo(carrito)
    
    contexto = {
        'carrito': carrito_completo,
    }
    
    return render(request, 'miapp/carrito.html', contexto)