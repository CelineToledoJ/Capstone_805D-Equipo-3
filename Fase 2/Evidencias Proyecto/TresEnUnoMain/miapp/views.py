from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from django.conf import settings
from .models import Producto, Categoria, Oferta, Cliente, Pedido, DetallePedido
from django.utils import timezone
from django.utils.html import strip_tags 

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
    CategoriaSerializer,
    ProductoSerializer,
    ProductoListSerializer,
    CarritoItemSerializer,
    CarritoSerializer,
    CheckoutSerializer,
    PedidoSerializer,
    PedidoListSerializer
)

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import transaction
from .serializers import CheckoutSerializer, PedidoSerializer, PedidoListSerializer


# ===== VISTAS HTML =====

def inicio(request):
    ofertas_activas = Oferta.objects.filter(
        fecha_fin__gte=timezone.now(), 
        fecha_inicio__lte=timezone.now(),
        activa=True
    )
    
    # ✅ CORREGIDO: categoria__nombre en lugar de id_categoria__nombre_categoria
    productos_destacados = Producto.objects.filter(
        categoria__nombre='Hortalizas',
        activo=True
    ).prefetch_related(
        Prefetch('ofertas', queryset=ofertas_activas, to_attr='ofertas_activas')
    ).order_by('?')[:3]

    contexto = {
        'productos': productos_destacados,
        'now': timezone.now(), 
    }
    return render(request, 'miapp/inicio.html', contexto)


def nosotros(request):
    return render(request, 'miapp/nosotros.html')


def listar_productos(request):
    ofertas_activas = Oferta.objects.filter(
        fecha_fin__gte=timezone.now(), 
        fecha_inicio__lte=timezone.now(),
        activa=True
    )
    
    # ✅ CORREGIDO: usar 'ofertas' en lugar de 'oferta_set'
    productos = Producto.objects.filter(activo=True).prefetch_related(
        Prefetch('ofertas', queryset=ofertas_activas, to_attr='ofertas_activas')
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
    producto = get_object_or_404(Producto, pk=producto_id)
    
    # ✅ CORREGIDO: producto en lugar de id_producto
    ofertas_activas = Oferta.objects.filter(
        producto=producto,
        fecha_fin__gte=timezone.now(),
        fecha_inicio__lte=timezone.now(),
        activa=True
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
    # ✅ CORREGIDO: categoria en lugar de id_categoria, y eliminado select_related('imagen')
    queryset = Producto.objects.filter(activo=True).select_related('categoria')
    serializer_class = ProductoListSerializer
    
    def get_queryset(self):
        """
        Opcionalmente permite filtrar por categoría
        Ejemplo: /api/public/products?categoria=Hortalizas
        """
        queryset = super().get_queryset()
        categoria = self.request.query_params.get('categoria', None)
        
        if categoria:
            # ✅ CORREGIDO: categoria__nombre en lugar de id_categoria__nombre_categoria
            queryset = queryset.filter(categoria__nombre__icontains=categoria)
        
        return queryset


class ProductoDetailAPIView(generics.RetrieveAPIView):
    """
    Endpoint GET /api/public/products/:id
    Obtiene el detalle completo de un producto específico (público)
    """
    # ✅ CORREGIDO: categoria en lugar de id_categoria, sin imagen, y ofertas en lugar de oferta_set
    queryset = Producto.objects.filter(activo=True).select_related('categoria').prefetch_related('ofertas')
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


# ===== FUNCIONES AUXILIARES PARA CARRITO =====

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
            # ✅ CORREGIDO: solo select_related('categoria'), sin imagen
            producto = Producto.objects.select_related('categoria').get(pk=producto_id)
            
            # Calcular precio (con oferta si existe)
            now = timezone.now()
            # ✅ CORREGIDO: ofertas en lugar de oferta_set
            oferta = producto.ofertas.filter(
                fecha_inicio__lte=now,
                fecha_fin__gte=now,
                activa=True
            ).first()
            
            precio = Decimal(str(oferta.precio_oferta)) if oferta else Decimal(str(producto.precio_unitario))
            subtotal = precio * cantidad
            
            # ✅ CORREGIDO: Obtener URL de imagen directamente
            imagen_url = None
            if producto.imagen:
                imagen_url = producto.imagen.url
            
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
            producto = Producto.objects.get(pk=producto_id, activo=True)
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
            producto = Producto.objects.get(pk=producto_id, activo=True)
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


# ===== FUNCIONES DE CORREO =====

def enviar_correo_confirmacion_pedido(pedido):
    """
    Envía correo de confirmación al cliente con instrucciones de pago
    """
    asunto = f'Pedido #{pedido.id} - Confirmación y Datos de Pago'
    
    # ✅ CORREGIDO: detalles en lugar de detallepedido_set
    detalles = pedido.detalles.all()
    
    # Contexto para el template
    contexto = {
        'pedido': pedido,
        'detalles': detalles,
        'banco': 'Banco Estado',
        'tipo_cuenta': 'Cuenta Corriente',
        'numero_cuenta': '123456789',
        'rut': '12.345.678-9',
        'titular': 'Tres En Uno SpA',
        'correo_contacto': 'ventas.tresenuno@gmail.com',
    }
    
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">¡Gracias por tu pedido!</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3>Pedido #{pedido.id}</h3>
                <p><strong>Fecha:</strong> {pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Total:</strong> ${pedido.total_pedido:,.0f}</p>
                <p><strong>Estado:</strong> {pedido.get_estado_pedido_display()}</p>
            </div>
            
            <h3>Productos:</h3>
            <ul>
    """
    
    for detalle in detalles:
        # ✅ CORREGIDO: producto en lugar de id_producto
        mensaje_html += f"<li>{detalle.cantidad} x {detalle.producto.nombre} - ${detalle.precio_compra:,.0f}</li>"
    
    mensaje_html += f"""
            </ul>
            
            <div style="background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3 style="margin-top: 0;">💳 Datos para Transferencia</h3>
                <p><strong>Banco:</strong> {contexto['banco']}</p>
                <p><strong>Tipo de Cuenta:</strong> {contexto['tipo_cuenta']}</p>
                <p><strong>Número de Cuenta:</strong> {contexto['numero_cuenta']}</p>
                <p><strong>RUT:</strong> {contexto['rut']}</p>
                <p><strong>Titular:</strong> {contexto['titular']}</p>
                <p><strong>Monto a transferir:</strong> ${pedido.total_pedido:,.0f}</p>
                <p style="color: #856404;"><strong>⚠️ Importante:</strong> Incluye el número de pedido #{pedido.id} en el mensaje de la transferencia.</p>
            </div>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">📦 Dirección de Envío</h3>
                <p>{pedido.direccion}</p>
                <p>{pedido.comuna}, {pedido.region}</p>
                {f'<p><strong>Referencia:</strong> {pedido.referencia_direccion}</p>' if pedido.referencia_direccion else ''}
            </div>
            
            <p>Una vez confirmado el pago, procesaremos tu pedido y te enviaremos la información de seguimiento.</p>
            
            <p>Si tienes alguna duda, contáctanos a: <a href="mailto:{contexto['correo_contacto']}">{contexto['correo_contacto']}</a></p>
            
            <hr style="margin: 30px 0;">
            <p style="color: #6c757d; font-size: 12px;">
                Tres En Uno - Cultivos Orgánicos<br>
                Este es un correo automático, por favor no respondas a este mensaje.
            </p>
        </body>
    </html>
    """
    
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        email = EmailMultiAlternatives(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            [pedido.correo_cliente]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False


def enviar_correo_admin_nuevo_pedido(pedido):
    """
    Notifica al administrador sobre un nuevo pedido
    """
    asunto = f'🛒 Nuevo Pedido #{pedido.id} - {pedido.nombre_cliente}'
    
    # ✅ CORREGIDO: detalles en lugar de detallepedido_set
    detalles = pedido.detalles.all()
    
    mensaje = f"""
    Se ha recibido un nuevo pedido en Tres En Uno.
    
    PEDIDO #{pedido.id}
    Fecha: {pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M')}
    Estado: {pedido.get_estado_pedido_display()}
    Total: ${pedido.total_pedido:,.0f}
    
    CLIENTE:
    Nombre: {pedido.nombre_cliente}
    Email: {pedido.correo_cliente}
    Teléfono: {pedido.telefono_cliente}
    
    DIRECCIÓN DE ENVÍO:
    {pedido.direccion}
    {pedido.comuna}, {pedido.region}
    {f'Referencia: {pedido.referencia_direccion}' if pedido.referencia_direccion else ''}
    
    PRODUCTOS:
    """
    
    for detalle in detalles:
        # ✅ CORREGIDO: producto en lugar de id_producto
        mensaje += f"\n- {detalle.cantidad} x {detalle.producto.nombre} - ${detalle.precio_compra:,.0f}"
    
    mensaje += f"""
    
    Para gestionar este pedido, ingresa al panel de administración:
    {settings.SITE_URL}/admin/miapp/pedido/{pedido.id}/
    """
    
    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            ['ventas.tresenuno@gmail.com'],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo al admin: {e}")
        return False


# ===== API VIEWS PARA CHECKOUT =====

class CheckoutAPIView(APIView):
    """
    POST /api/checkout - Procesar el checkout y crear el pedido
    """
    
    @transaction.atomic
    def post(self, request):
        """Procesa el checkout y crea el pedido"""
        
        # Validar datos del formulario
        serializer = CheckoutSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener el carrito
        carrito = obtener_carrito(request)
        
        if not carrito.get('items') or len(carrito['items']) == 0:
            return Response({
                'error': 'El carrito está vacío'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calcular carrito completo
        carrito_completo = calcular_carrito_completo(carrito)
        
        # Crear el pedido
        datos_pedido = serializer.validated_data
        
        pedido = Pedido.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            nombre_cliente=datos_pedido['nombre_cliente'],
            correo_cliente=datos_pedido['correo_cliente'],
            telefono_cliente=datos_pedido['telefono_cliente'],
            direccion=datos_pedido['direccion'],
            region=datos_pedido['region'],
            comuna=datos_pedido['comuna'],
            codigo_postal=datos_pedido.get('codigo_postal', ''),
            referencia_direccion=datos_pedido.get('referencia_direccion', ''),
            notas_pedido=datos_pedido.get('notas_pedido', ''),
            metodo_pago=datos_pedido.get('metodo_pago', 'transferencia'),
            total_pedido=carrito_completo['total'],
            estado_pedido='pendiente_pago'
        )
        
        # Crear detalles del pedido y descontar stock
        for item in carrito_completo['items']:
            producto = Producto.objects.get(pk=item['producto_id'])
            
            # Verificar stock nuevamente
            if producto.stock_disponible < item['cantidad']:
                raise Exception(f'Stock insuficiente para {producto.nombre}')
            
            # ✅ CORREGIDO: pedido y producto en lugar de id_pedido e id_producto
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item['cantidad'],
                precio_compra=item['precio_unitario']
            )
            
            # Descontar stock usando el método del modelo
            producto.reducir_stock(item['cantidad'])
        
        # Limpiar el carrito
        request.session['carrito'] = {'items': {}}
        request.session.modified = True
        
        # Enviar correos
        enviar_correo_confirmacion_pedido(pedido)
        enviar_correo_admin_nuevo_pedido(pedido)
        
        # Serializar el pedido para la respuesta
        pedido_serializer = PedidoSerializer(pedido, context={'request': request})
        
        return Response({
            'message': 'Pedido creado exitosamente',
            'pedido': pedido_serializer.data
        }, status=status.HTTP_201_CREATED)


class MisPedidosAPIView(generics.ListAPIView):
    """
    GET /api/mis-pedidos - Lista los pedidos del usuario autenticado
    """
    serializer_class = PedidoListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-fecha_pedido')


class DetallePedidoAPIView(generics.RetrieveAPIView):
    """
    GET /api/pedidos/<id> - Obtiene el detalle de un pedido específico
    """
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user)


# ===== VISTAS HTML =====

def checkout(request):
    """
    Vista que renderiza la página de checkout
    URL: /checkout/
    """
    carrito = obtener_carrito(request)
    carrito_completo = calcular_carrito_completo(carrito)
    
    if not carrito_completo['items']:
        from django.shortcuts import redirect
        return redirect('listar_productos')
    
    # Si el usuario está autenticado, pre-llenar datos
    datos_usuario = {}
    if request.user.is_authenticated:
        datos_usuario = {
            'nombre': request.user.nombre,
            'correo': request.user.correo,
            'telefono': request.user.telefono or '',
        }
    
    contexto = {
        'carrito': carrito_completo,
        'datos_usuario': datos_usuario,
    }
    
    return render(request, 'miapp/checkout.html', contexto)


def confirmacion_pedido(request, pedido_id):
    """
    Vista que muestra la confirmación del pedido
    URL: /pedido-confirmado/<id>/
    """
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    # ✅ CORREGIDO: detalles en lugar de detallepedido_set
    detalles = pedido.detalles.all()
    
    # Calcular subtotales para cada detalle
    detalles_con_subtotal = []
    for detalle in detalles:
        detalles_con_subtotal.append({
            'detalle': detalle,
            'subtotal': detalle.subtotal  # Usa la property del modelo
        })
    
    contexto = {
        'pedido': pedido,
        'detalles': detalles,
        'detalles_con_subtotal': detalles_con_subtotal,
    }
    
    return render(request, 'miapp/confirmacion_pedido.html', contexto)


def mis_pedidos(request):
    """
    Vista que muestra los pedidos del usuario autenticado
    URL: /mis-pedidos/
    """
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login-form')
    
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    contexto = {
        'pedidos': pedidos,
    }
    
    return render(request, 'miapp/mis_pedidos.html', contexto)

class CategoriaListAPIView(generics.ListAPIView):
    """
    Endpoint GET /api/public/categories
    Lista todas las categorías activas (público)
    """
    queryset = Categoria.objects.filter(activa=True).order_by('nombre')
    serializer_class = CategoriaSerializer
    
    def get_queryset(self):
        """Retorna solo categorías activas con productos"""
        queryset = super().get_queryset()
        # Opcional: solo mostrar categorías que tengan productos
        # queryset = queryset.annotate(
        #     total_productos=Count('productos', filter=Q(productos__activo=True))
        # ).filter(total_productos__gt=0)
        return queryset