# miapp/models.py
from django.db import models

# Tabla Categorias
class Categoria(models.Model):
    # id_categoria Django lo crea automáticamente (se llamará 'id')
    nombre_categoria = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_categoria

# Tabla Productos
class Producto(models.Model):
    # id_producto Django lo crea automáticamente
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)
    stock_disponible = models.IntegerField()
    # Relación: Un producto pertenece a una categoría
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Tabla Clientes
class Cliente(models.Model):
    # id_cliente Django lo crea automáticamente
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(unique=True) # unique=True para que no se repitan correos
    telefono = models.CharField(max_length=20, blank=True, null=True)
    contraseña_hash = models.CharField(max_length=255) # Django tiene un mejor sistema para esto
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# Tabla Pedidos
class Pedido(models.Model):
    # id_pedido Django lo crea automáticamente
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pedido = models.CharField(max_length=50, default='Pendiente')
    # Relación: Un pedido puede ser de un cliente registrado (o no, si es invitado)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    # Campos para invitados
    nombre_invitado = models.CharField(max_length=255, null=True, blank=True)
    correo_invitado = models.EmailField(null=True, blank=True)

    def __str__(self):
        if self.id_cliente:
            return f"Pedido de {self.id_cliente.nombre}"
        return f"Pedido de invitado {self.nombre_invitado}"

# Tabla DetallePedidos
class DetallePedido(models.Model):
    # id_detalle Django lo crea automáticamente
    cantidad = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    # Relaciones: El detalle conecta un pedido con un producto
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cantidad} x {self.id_producto.nombre} en Pedido {self.id_pedido.id}"

# Tabla Ofertas
class Oferta(models.Model):
    # id_oferta Django lo crea automáticamente
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    # Relación: La oferta es para un producto específico
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return f"Oferta para {self.id_producto.nombre} a ${self.precio_oferta}"