from rest_framework import serializers
# Ya no necesitamos make_password, check_password, ya que AbstractBaseUser los incluye en el modelo
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