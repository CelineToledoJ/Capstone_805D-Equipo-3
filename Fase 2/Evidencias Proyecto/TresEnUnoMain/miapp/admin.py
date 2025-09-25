from django.contrib import admin
from .models import Categoria, Producto, Cliente, Pedido, DetallePedido, Oferta, Imagen # <-- ¡Agrega Imagen aquí!
from django.utils.html import format_html

# Models

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista de productos
    list_display = ('nombre', 'precio_unitario', 'stock_disponible', 'id_categoria', 'imagen_preview')
    
    # Campos que se muestran en el formulario de edición
    fields = ('nombre', 'descripcion', 'precio_unitario', 'unidad_medida', 'stock_disponible', 'id_categoria', 'imagen', 'imagen_preview')
    
    # Campos de solo lectura, como la previsualización de la imagen
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        # Asegúrate de acceder a la URL de la imagen a través del modelo Imagen
        if obj.imagen and obj.imagen.imagen: # <-- Asegura que ambos campos existan
            return format_html('<img src="{}" width="100" height="100" />', obj.imagen.imagen.url)
        return "(Sin imagen)"
    
    imagen_preview.short_description = 'Previsualización de Imagen'

admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Oferta)
admin.site.register(Imagen)