from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 

# ------------------------------------------------
# MANAGER PERSONALIZADO
# ------------------------------------------------
class ClienteManager(BaseUserManager):
    """
    Manager de usuario personalizado donde el campo 'correo' es el identificador único.
    """
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
# MODELO CLIENTE (CON ALIAS DE COMPATIBILIDAD)
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

    # ⭐ CORRECCIÓN CLAVE: Alias para Django Auth ⭐
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

    # Ya no es necesario incluir has_perm o has_module_perms si heredas de PermissionsMixin
    # ya que esta clase los implementa automáticamente.
    
# ------------------------------------------------
# RESTO DE LOS MODELOS (SIN CAMBIOS)
# ------------------------------------------------

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
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pedido = models.CharField(max_length=50, default='Pendiente')
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    nombre_invitado = models.CharField(max_length=255, null=True, blank=True)
    correo_invitado = models.EmailField(null=True, blank=True)

    class Meta:
        db_table = 'pedidos'

    def __str__(self):
        if self.usuario:
            return f"Pedido de {self.usuario.nombre or self.usuario.correo}" 
        return f"Pedido de invitado {self.nombre_invitado}"

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