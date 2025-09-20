from django.contrib import admin
from .models import Categoria, Producto, Cliente, Pedido, DetallePedido, Oferta

# Registra tus modelos aquí.

admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Oferta)