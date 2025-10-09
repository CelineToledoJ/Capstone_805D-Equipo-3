from rest_framework import serializers
from rest_framework import exceptions 
from .models import Cliente, Producto, Imagen, Categoria, Oferta  
from django.utils import timezone  

class ClienteRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = Cliente
        fields = ('nombre', 'correo', 'telefono', 'password') 

    def create(self, validated_data):
        """
        Sobrescribe el método create() para usar la gestión de contraseñas de AbstractBaseUser.
        """
        # ⭐ CORRECCIÓN 1: Extraer y usar set_password() de AbstractBaseUser ⭐
        password = validated_data.pop('password')
        
        # El modelo Cliente ya no tiene 'contraseña_hash', AbstractBaseUser lo maneja.
        cliente = Cliente.objects.create(**validated_data)
        
        # set_password hashea la contraseña y la guarda en el campo 'password'.
        cliente.set_password(password)
        cliente.save() 
        
        return cliente

class ClienteLoginSerializer(serializers.Serializer):
    """
    Serializador para recibir credenciales de login y validar al cliente.
    """
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        correo = data.get('correo')
        password = data.get('password')
        
        if not correo or not password:
            raise exceptions.AuthenticationFailed('Debe proporcionar correo y contraseña.')

        try:
            # Busca al cliente.
            cliente = Cliente.objects.get(correo=correo)
        except Cliente.DoesNotExist:
            raise exceptions.AuthenticationFailed('Credenciales inválidas.')

        # ⭐ CORRECCIÓN 2: Usar el método check_password() de AbstractBaseUser ⭐
        # Este método verifica el hash guardado en el campo 'password' de forma segura.
        if not cliente.check_password(password):
            raise exceptions.AuthenticationFailed('Credenciales inválidas.')

        data['cliente'] = cliente
        return data

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador simple para exponer datos del cliente (nombre, correo, etc.)
    al frontend cuando está autenticado.
    """
    class Meta:
        model = Cliente
        fields = ('id', 'nombre', 'correo', 'telefono') 
        read_only_fields = fields

class ImagenSerializer(serializers.ModelSerializer):
    """Serializer para las imágenes de productos"""
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Imagen
        fields = ['id', 'nombre', 'imagen', 'imagen_url']
    
    def get_imagen_url(self, obj):
        """Retorna la URL completa de la imagen"""
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para categorías"""
    class Meta:
        model = Categoria
        fields = ['id', 'nombre_categoria', 'descripcion']


class OfertaSerializer(serializers.ModelSerializer):
    """Serializer para ofertas activas"""
    esta_activa = serializers.SerializerMethodField()
    
    class Meta:
        model = Oferta
        fields = ['id', 'precio_oferta', 'fecha_inicio', 'fecha_fin', 'esta_activa']
    
    def get_esta_activa(self, obj):
        """Verifica si la oferta está activa en este momento"""
        now = timezone.now()
        return obj.fecha_inicio <= now <= obj.fecha_fin


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer completo para mostrar un producto con toda su información"""
    categoria = CategoriaSerializer(source='id_categoria', read_only=True)
    imagen_principal = ImagenSerializer(source='imagen', read_only=True)
    ofertas_activas = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()
    tiene_oferta = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio_unitario',
            'unidad_medida',
            'stock_disponible',
            'categoria',
            'imagen_principal',
            'ofertas_activas',
            'precio_final',
            'tiene_oferta'
        ]
    
    def get_ofertas_activas(self, obj):
        """Obtiene las ofertas activas del producto"""
        now = timezone.now()
        ofertas = obj.oferta_set.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        )
        return OfertaSerializer(ofertas, many=True).data
    
    def get_precio_final(self, obj):
        """Calcula el precio final (con oferta si existe)"""
        now = timezone.now()
        oferta = obj.oferta_set.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        ).first()
        
        if oferta:
            return float(oferta.precio_oferta)
        return float(obj.precio_unitario)
    
    def get_tiene_oferta(self, obj):
        """Verifica si el producto tiene ofertas activas"""
        now = timezone.now()
        return obj.oferta_set.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        ).exists()


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de productos"""
    imagen_url = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()
    tiene_oferta = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'precio_unitario',
            'precio_final',
            'tiene_oferta',
            'unidad_medida',
            'stock_disponible',
            'imagen_url'
        ]
    
    def get_imagen_url(self, obj):
        """Retorna la URL de la imagen principal"""
        if obj.imagen and obj.imagen.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.imagen.url)
            return obj.imagen.imagen.url
        return None
    
    def get_precio_final(self, obj):
        """Calcula el precio final (con oferta si existe)"""
        now = timezone.now()
        oferta = obj.oferta_set.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        ).first()
        
        if oferta:
            return float(oferta.precio_oferta)
        return float(obj.precio_unitario)
    
    def get_tiene_oferta(self, obj):
        """Verifica si el producto tiene ofertas activas"""
        now = timezone.now()
        return obj.oferta_set.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        ).exists()