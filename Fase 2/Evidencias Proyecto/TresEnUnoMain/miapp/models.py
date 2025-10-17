from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 


class ClienteManager(BaseUserManager):
    
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El Cliente debe tener un correo.')
        
        correo = self.normalize_email(correo)
        cliente = self.model(correo=correo, **extra_fields)
        
        cliente.set_password(password) 
        cliente.save(using=self._db)
        return cliente

    def create_superuser(self, correo, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
            
        return self.create_user(correo, password, **extra_fields)

# ------------------------------------------------
# MODELO CLIENTE 
# ------------------------------------------------
class Cliente(AbstractBaseUser, PermissionsMixin):
    
    # ------------------ Campos de Datos ------------------
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # ------------------ Campos de Permisos ------------------
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    @property
    def email(self):
        """Permite que el sistema de autenticación de Django acceda a 'correo' usando el atributo 'email'."""
        return self.correo
    # ----------------------------------------------------------------------

    # ------------------ Configuración de Autenticación ------------------
    USERNAME_FIELD = 'correo' 
    REQUIRED_FIELDS = ['nombre'] 

    objects = ClienteManager() 

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return self.correo

class Imagen(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre_categoria

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    precio_unitario = models.IntegerField()
    unidad_medida = models.CharField(max_length=20)
    stock_disponible = models.IntegerField()
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    # Estados del pedido
    ESTADOS = [
        ('pendiente_pago', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('preparando', 'Preparando Envío'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Métodos de pago
    METODOS_PAGO = [
        ('transferencia', 'Transferencia Bancaria'),
        ('webpay', 'Webpay (Próximamente)'),
    ]
    
    # Información básica del pedido
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pedido = models.CharField(max_length=50, choices=ESTADOS, default='pendiente_pago')
    metodo_pago = models.CharField(max_length=50, choices=METODOS_PAGO, default='transferencia')
    
    # Cliente registrado o invitado
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Datos del cliente (para invitados o para guardar snapshot)
    nombre_cliente = models.CharField(max_length=255)
    correo_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)
    
    # Dirección de envío
    direccion = models.CharField(max_length=500)
    region = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    referencia_direccion = models.TextField(blank=True, null=True, help_text="Referencias adicionales para encontrar la dirección")
    
    # Información adicional
    notas_pedido = models.TextField(blank=True, null=True, help_text="Notas o comentarios del cliente")
    
    # Datos de seguimiento
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    numero_seguimiento = models.CharField(max_length=100, blank=True, null=True, help_text="Número de seguimiento del envío")
    
    # Campos legacy (mantener compatibilidad)
    nombre_invitado = models.CharField(max_length=255, null=True, blank=True)
    correo_invitado = models.EmailField(null=True, blank=True)

    class Meta:
        db_table = 'pedidos'
        ordering = ['-fecha_pedido']

    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente} - {self.get_estado_pedido_display()}"
    
    def es_invitado(self):
        """Retorna True si el pedido fue hecho por un invitado"""
        return self.usuario is None
    
    def puede_cancelar(self):
        """Determina si el pedido puede ser cancelado"""
        return self.estado_pedido in ['pendiente_pago', 'pagado']
    
    def marcar_como_pagado(self):
        """Marca el pedido como pagado y registra la fecha"""
        from django.utils import timezone
        self.estado_pedido = 'pagado'
        self.fecha_pago = timezone.now()
        self.save()
    
    def marcar_como_enviado(self, numero_seguimiento=None):
        """Marca el pedido como enviado"""
        from django.utils import timezone
        self.estado_pedido = 'enviado'
        self.fecha_envio = timezone.now()
        if numero_seguimiento:
            self.numero_seguimiento = numero_seguimiento
        self.save()

class DetallePedido(models.Model):
    cantidad = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    class Meta:
        db_table = 'detalle_pedidos'

    def __str__(self):
        return f"{self.cantidad} x {self.id_producto.nombre} en Pedido {self.id_pedido.id}"

class Oferta(models.Model):
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ofertas'

    def __str__(self):
        return f"Oferta para {self.id_producto.nombre} a ${self.precio_oferta}"