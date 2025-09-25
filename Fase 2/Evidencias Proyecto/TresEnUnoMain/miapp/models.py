from django.db import models
from django.contrib.auth.models import User

# El modelo 'Imagen' debe definirse antes de ser utilizado por 'Producto'.
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

class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    contraseña_hash = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pedido = models.CharField(max_length=50, default='Pendiente')
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    nombre_invitado = models.CharField(max_length=255, null=True, blank=True)
    correo_invitado = models.EmailField(null=True, blank=True)

    class Meta:
        db_table = 'pedidos'

    def __str__(self):
        if self.usuario:
            return f"Pedido de {self.usuario.get_full_name() or self.usuario.username}"
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