from rest_framework import serializers
from .models import Paciente
from django.contrib.auth.models import User
import re

class PacienteSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(write_only=True, required=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    nombre_completo = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Paciente
        fields = ['id', 'user_id', 'nombre_completo', 'nombre', 'dni', 
                 'telefono', 'direccion', 'fecha_nacimiento',
                 'password', 'confirm_password']
        read_only_fields = ['id', 'user_id', 'nombre_completo']
        extra_kwargs = {
            'dni': {'required': True},
            'telefono': {'required': True},
            'direccion': {'required': True},
        }
    
    def get_nombre_completo(self, obj):
        if obj.user:
            nombre_completo = f"{obj.user.first_name} {obj.user.last_name}".strip()
            return nombre_completo if nombre_completo else f"Usuario {obj.user.id}"
        return "Usuario no asignado"

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        
        dni = data.get('dni')
        if dni and Paciente.objects.filter(dni=dni).exists():
            raise serializers.ValidationError({"dni": "Ya existe un paciente con este DNI."})
        
        dni_regex = r'^\d{3}-\d{6}-\d{4}[A-Z]?$'
        if not re.match(dni_regex, dni):
            raise serializers.ValidationError({"dni": "Formato de DNI inválido. Use: 000-000000-0000A"})
        
        return data

    def create(self, validated_data):
        nombre = validated_data.pop('nombre')
        dni = validated_data.pop('dni')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        
        nombres = nombre.split(' ')
        if len(nombres) >= 2:
            base_username = f"{nombres[0].lower()}.{nombres[1].lower()}"
        else:
            base_username = nombres[0].lower()
        
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nombre.split(' ')[0] if ' ' in nombre else nombre,
            last_name=nombre.split(' ')[1] if ' ' in nombre else '',
            email=f"{username}@clinica.com"
        )
        
        paciente = Paciente.objects.create(user=user, **validated_data)
        
        from autenticacion.models import PerfilUsuario
        if hasattr(user, 'perfil'):
            user.perfil.tipo_usuario = 'paciente'
            user.perfil.save()
        
        return paciente

    def update(self, instance, validated_data):
        nombre = validated_data.pop('nombre', None)
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)
        dni = validated_data.get('dni', instance.dni)
        
        if password:
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
            user = instance.user
            user.set_password(password)
            user.save()
        
        if nombre:
            user = instance.user
            user.first_name = nombre.split(' ')[0] if ' ' in nombre else nombre
            user.last_name = nombre.split(' ')[1] if ' ' in nombre else ''
            user.save()
        
        if dni and dni != instance.dni:
            if Paciente.objects.filter(dni=dni).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"dni": "Ya existe un paciente con este DNI."})
            
            user = instance.user
            user.username = f"paciente_{dni}"
            user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation.get('nombre_completo'):
            representation['nombre_completo'] = self.get_nombre_completo(instance)
        return representation