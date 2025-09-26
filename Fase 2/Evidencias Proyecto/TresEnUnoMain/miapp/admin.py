from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone  # Importamos timezone para la lógica de Oferta
from .models import Categoria, Producto, Cliente, Pedido, DetallePedido, Oferta, Imagen

# Config modelos secundarios 
@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen_preview', 'id')
    readonly_fields = ('imagen_preview',)
    search_fields = ('nombre',)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.imagen.url)
        return "No Image"
    imagen_preview.short_description = 'Previsualización'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria', 'descripcion_corta')
    search_fields = ('nombre_categoria',)

    def descripcion_corta(self, obj):
        if obj.descripcion:
            return f"{obj.descripcion[:50]}..." if len(obj.descripcion) > 50 else obj.descripcion
        return ""
    descripcion_corta.short_description = 'Descripción'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'correo', 'telefono')
    list_filter = ('fecha_registro',)
    readonly_fields = ('fecha_registro', 'contraseña_hash') # Esto hace que el hash de la password no sea editable, no cambiar.


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'precio_oferta', 'fecha_inicio', 'fecha_fin', 'es_activa')
    list_filter = ('fecha_inicio', 'fecha_fin')
    search_fields = ('id_producto__nombre',)

    def es_activa(self, obj):
        now = timezone.now()
        return obj.fecha_inicio <= now and obj.fecha_fin >= now
    es_activa.boolean = True
    es_activa.short_description = 'Activa'

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_unitario', 'stock_disponible', 'id_categoria', 'imagen_preview', 'en_oferta')
    
    list_filter = ('id_categoria', 'unidad_medida', 'stock_disponible')
    search_fields = ('nombre', 'descripcion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'id_categoria', 'unidad_medida')
        }),
        ('Inventario y Precios', {
            'fields': ('precio_unitario', 'stock_disponible')
        }),
        ('Imagen', {
            'fields': ('imagen', 'imagen_preview'),
            'description': 'Seleccione la imagen ya cargada o súbala en el menú "Imágenes".'
        }),
    )
    
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        if obj.imagen and obj.imagen.imagen:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />', obj.imagen.imagen.url)
        return "(Sin foto)"
    imagen_preview.short_description = 'Foto'
    
    def en_oferta(self, obj):
        now = timezone.now()
        return obj.oferta_set.filter(fecha_inicio__lte=now, fecha_fin__gte=now).exists()
    en_oferta.boolean = True
    en_oferta.short_description = 'Oferta Activa'

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0  
    readonly_fields = ('precio_compra', 'id_producto') 
    fields = ('id_producto', 'cantidad', 'precio_compra')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_pedido', 'estado_pedido', 'total_pedido', 'mostrar_cliente')
    
    list_filter = ('estado_pedido', 'fecha_pedido')
    search_fields = ('usuario__username', 'nombre_invitado', 'correo_invitado')
    
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Estado y Totales', {
            'fields': ('estado_pedido', 'total_pedido')
        }),
        ('Información del Cliente', {
            'fields': ('usuario', 'nombre_invitado', 'correo_invitado'),
            'description': 'El campo "Usuario" se usa para clientes registrados. Los campos de invitado se usan para compras sin cuenta.'
        }),
        ('Fechas', {
            'fields': ('fecha_pedido',),
            'classes': ('collapse',), 
        }),
    )
    
    readonly_fields = ('total_pedido', 'fecha_pedido')

    def mostrar_cliente(self, obj):
        if obj.usuario:
            return f"Usuario: {obj.usuario.username}"
        if obj.nombre_invitado:
            return f"Invitado: {obj.nombre_invitado}"
        return "N/A"
    mostrar_cliente.short_description = 'Cliente'


