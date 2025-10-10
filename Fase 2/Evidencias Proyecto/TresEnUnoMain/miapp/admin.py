from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Categoria, Producto, Cliente, Pedido, DetallePedido, Oferta, Imagen

# ===== CONFIGURACIÓN PARA IMAGEN =====
@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'imagen_preview', 'imagen')
    list_display_links = ('id', 'nombre')
    readonly_fields = ('imagen_preview',)
    search_fields = ('nombre', 'id')
    ordering = ('-id',)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px; object-fit: cover;" />', obj.imagen.url)
        return "Sin Imagen"
    imagen_preview.short_description = 'Vista Previa'


# ===== CONFIGURACIÓN PARA CATEGORÍA =====
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_categoria', 'descripcion_corta', 'total_productos')
    list_display_links = ('id', 'nombre_categoria')
    search_fields = ('nombre_categoria', 'id')
    ordering = ('-id',)

    def descripcion_corta(self, obj):
        if obj.descripcion:
            return f"{obj.descripcion[:50]}..." if len(obj.descripcion) > 50 else obj.descripcion
        return ""
    descripcion_corta.short_description = 'Descripción'
    
    def total_productos(self, obj):
        return obj.producto_set.count()
    total_productos.short_description = 'Total Productos'


# ===== CONFIGURACIÓN PARA CLIENTE =====
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo', 'telefono', 'fecha_registro', 'is_active', 'is_staff')
    list_display_links = ('id', 'nombre', 'correo')
    search_fields = ('nombre', 'correo', 'telefono', 'id')
    list_filter = ('fecha_registro', 'is_active', 'is_staff')
    readonly_fields = ('fecha_registro', 'last_login')
    ordering = ('-id',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('correo', 'nombre', 'telefono')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_registro', 'last_login')
        }),
    )


# ===== CONFIGURACIÓN PARA OFERTA =====
@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_producto', 'precio_oferta', 'fecha_inicio', 'fecha_fin', 'es_activa')
    list_display_links = ('id', 'id_producto')
    list_filter = ('fecha_inicio', 'fecha_fin')
    search_fields = ('id_producto__nombre', 'id')
    date_hierarchy = 'fecha_inicio'
    ordering = ('-id',)

    def es_activa(self, obj):
        now = timezone.now()
        return obj.fecha_inicio <= now and obj.fecha_fin >= now
    es_activa.boolean = True
    es_activa.short_description = 'Activa'


# ===== CONFIGURACIÓN PARA PRODUCTO =====
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio_unitario', 'stock_disponible', 'unidad_medida', 'id_categoria', 'imagen_preview', 'en_oferta')
    list_display_links = ('id', 'nombre')
    list_filter = ('id_categoria', 'unidad_medida', 'stock_disponible')
    search_fields = ('nombre', 'descripcion', 'id')
    ordering = ('-id',)
    list_per_page = 20
    
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
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px; object-fit: cover;" />', obj.imagen.imagen.url)
        return "(Sin foto)"
    imagen_preview.short_description = 'Foto'
    
    def en_oferta(self, obj):
        now = timezone.now()
        return obj.oferta_set.filter(fecha_inicio__lte=now, fecha_fin__gte=now).exists()
    en_oferta.boolean = True
    en_oferta.short_description = 'Oferta Activa'


# ===== CONFIGURACIÓN PARA DETALLE PEDIDO (INLINE) =====
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('precio_compra', 'id_producto')
    fields = ('id_producto', 'cantidad', 'precio_compra')


# ===== CONFIGURACIÓN PARA PEDIDO =====
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mostrar_cliente', 'fecha_pedido', 'estado_pedido', 'total_pedido')
    list_display_links = ('id', 'mostrar_cliente')
    list_filter = ('estado_pedido', 'fecha_pedido')
    search_fields = ('usuario__nombre', 'usuario__correo', 'nombre_invitado', 'correo_invitado', 'id')
    date_hierarchy = 'fecha_pedido'
    inlines = [DetallePedidoInline]
    ordering = ('-id',)
    
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
            return f"{obj.usuario.nombre} ({obj.usuario.correo})"
        if obj.nombre_invitado:
            return f"Invitado: {obj.nombre_invitado} ({obj.correo_invitado})"
        return "N/A"
    mostrar_cliente.short_description = 'Cliente'


# ===== CONFIGURACIÓN PARA DETALLE PEDIDO =====
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_pedido', 'id_producto', 'cantidad', 'precio_compra', 'subtotal')
    list_display_links = ('id',)
    list_filter = ('id_pedido__estado_pedido',)
    search_fields = ('id_pedido__id', 'id_producto__nombre', 'id')
    ordering = ('-id',)
    
    def subtotal(self, obj):
        total = obj.cantidad * obj.precio_compra
        return f'${total:,.0f}'
    subtotal.short_description = 'Subtotal'


# ===== PERSONALIZACIÓN DEL SITIO ADMIN =====
admin.site.site_header = "Tres En Uno - Administración"
admin.site.site_title = "Tres En Uno Admin"
admin.site.index_title = "Panel de Administración - Sistema de Gestión"