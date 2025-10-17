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
    list_display = ('id', 'nombre_cliente', 'correo_cliente', 'fecha_pedido', 'estado_badge', 'total_pedido', 'metodo_pago')
    list_display_links = ('id', 'nombre_cliente')
    list_filter = ('estado_pedido', 'metodo_pago', 'fecha_pedido')
    search_fields = ('nombre_cliente', 'correo_cliente', 'telefono_cliente', 'id')
    date_hierarchy = 'fecha_pedido'
    inlines = [DetallePedidoInline]
    ordering = ('-id',)
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id', 'fecha_pedido', 'estado_pedido', 'metodo_pago', 'total_pedido')
        }),
        ('Información del Cliente', {
            'fields': ('usuario', 'nombre_cliente', 'correo_cliente', 'telefono_cliente')
        }),
        ('Dirección de Envío', {
            'fields': ('direccion', 'region', 'comuna', 'codigo_postal', 'referencia_direccion')
        }),
        ('Seguimiento', {
            'fields': ('numero_seguimiento', 'fecha_pago', 'fecha_envio', 'fecha_entrega'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notas_pedido',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('id', 'fecha_pedido', 'total_pedido', 'fecha_pago', 'fecha_envio', 'fecha_entrega')
    
    def estado_badge(self, obj):
        colores = {
            'pendiente_pago': '#ffc107',
            'pagado': '#28a745',
            'preparando': '#17a2b8',
            'enviado': '#007bff',
            'completado': '#6c757d',
            'cancelado': '#dc3545',
        }
        color = colores.get(obj.estado_pedido, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_pedido_display()
        )
    estado_badge.short_description = 'Estado'
    
    actions = ['marcar_como_pagado', 'marcar_como_enviado', 'marcar_como_completado', 'cancelar_pedidos']
    
    def marcar_como_pagado(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(estado_pedido='pendiente_pago').update(
            estado_pedido='pagado',
            fecha_pago=timezone.now()
        )
        self.message_user(request, f'{updated} pedido(s) marcado(s) como pagado.')
    marcar_como_pagado.short_description = "✅ Marcar como Pagado"
    
    def marcar_como_enviado(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(estado_pedido__in=['pagado', 'preparando']).update(
            estado_pedido='enviado',
            fecha_envio=timezone.now()
        )
        self.message_user(request, f'{updated} pedido(s) marcado(s) como enviado.')
    marcar_como_enviado.short_description = "📦 Marcar como Enviado"
    
    def marcar_como_completado(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(estado_pedido='enviado').update(
            estado_pedido='completado',
            fecha_entrega=timezone.now()
        )
        self.message_user(request, f'{updated} pedido(s) marcado(s) como completado.')
    marcar_como_completado.short_description = "✔️ Marcar como Completado"
    
    def cancelar_pedidos(self, request, queryset):
        updated = queryset.filter(estado_pedido__in=['pendiente_pago', 'pagado']).update(
            estado_pedido='cancelado'
        )
        self.message_user(request, f'{updated} pedido(s) cancelado(s).')
    cancelar_pedidos.short_description = "❌ Cancelar Pedidos"


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