# autenticacion/serializers.py - COMPLETO
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from .models import PerfilUsuario
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.CharField(source='perfil.tipo_usuario', read_only=True)
    perfil_id = serializers.IntegerField(source='perfil.id', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'is_staff', 'is_superuser', 'date_joined',
                  'tipo_usuario', 'perfil_id']
        read_only_fields = ['id', 'date_joined']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Intento de login para usuario: {username}")
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    logger.warning(f"Usuario {username} desactivado")
                    raise serializers.ValidationError("Usuario desactivado.")
                
                if not hasattr(user, 'perfil'):
                    logger.warning(f"Usuario {username} no tiene perfil. Creando...")
                    try:
                        PerfilUsuario.objects.create(user=user)
                    except Exception as e:
                        logger.error(f"Error creando perfil: {str(e)}")
                
                data['user'] = user
                logger.info(f"Login exitoso para {username}")
            else:
                logger.warning(f"Credenciales inválidas para {username}")
                raise serializers.ValidationError("Credenciales inválidas.")
        else:
            logger.warning("Faltan credenciales")
            raise serializers.ValidationError("Debe proporcionar username y password.")
        
        return data

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    tipo_usuario = serializers.ChoiceField(choices=PerfilUsuario.TIPO_USUARIO_CHOICES, required=True)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'password', 'password2', 'tipo_usuario']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Este nombre de usuario ya existe."})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Este correo electrónico ya está registrado."})
        
        return attrs
    
    def create(self, validated_data):
        tipo_usuario = validated_data.pop('tipo_usuario')
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        user.perfil.tipo_usuario = tipo_usuario
        user.perfil.save()
        
        grupo, created = Group.objects.get_or_create(name=tipo_usuario)
        user.groups.add(grupo)
        
        return user

class CambioPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})
        return data

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = PerfilUsuario
        fields = ['id', 'user_info', 'tipo_usuario', 'telefono', 
                  'direccion', 'fecha_nacimiento', 'creado_en', 'actualizado_en']
        read_only_fields = ['id', 'creado_en', 'actualizado_en']