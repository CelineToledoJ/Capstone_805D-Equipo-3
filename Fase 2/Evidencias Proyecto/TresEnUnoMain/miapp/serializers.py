from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import exceptions
from .models import Cliente

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
        Sobrescribe el método create() para hashear la contraseña antes de guardar.
        """
        password = validated_data.pop('password')
        
        validated_data['contraseña_hash'] = make_password(password)
        
        cliente = Cliente.objects.create(**validated_data)
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
            cliente = Cliente.objects.get(correo=correo)
        except Cliente.DoesNotExist:
            raise exceptions.AuthenticationFailed('Credenciales inválidas.')

        if not check_password(password, cliente.contraseña_hash):
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