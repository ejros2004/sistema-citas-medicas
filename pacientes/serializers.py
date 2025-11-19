from rest_framework import serializers
from .models import Paciente
from django.contrib.auth.models import User

class PacienteSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(write_only=True, required=False)  # Para crear desde frontend
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    nombre_completo = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Paciente
        fields = ['id', 'user_id', 'nombre_completo', 'nombre', 'dni', 'telefono', 'direccion', 'fecha_nacimiento']
        read_only_fields = ['id', 'user_id', 'nombre_completo']
        extra_kwargs = {
            'dni': {'required': True},
            'telefono': {'required': True},
            'direccion': {'required': True},
        }
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del usuario"""
        if obj.user:
            nombre_completo = f"{obj.user.first_name} {obj.user.last_name}".strip()
            return nombre_completo if nombre_completo else f"Usuario {obj.user.id}"
        return "Usuario no asignado"

    def create(self, validated_data):
        """
        Crear paciente automáticamente con usuario
        """
        # Extraer el nombre del frontend
        nombre = validated_data.pop('nombre', None)
        
        if not nombre:
            raise serializers.ValidationError({"nombre": "Este campo es requerido para crear un paciente."})
        
        # Verificar si el DNI ya existe
        dni = validated_data['dni']
        if Paciente.objects.filter(dni=dni).exists():
            raise serializers.ValidationError({"dni": "Ya existe un paciente con este DNI."})
        
        # Crear usuario automáticamente
        username = f"paciente_{dni}"
        user = User.objects.create_user(
            username=username,
            password='TempPassword123!',  # Password temporal
            first_name=nombre.split(' ')[0] if ' ' in nombre else nombre,
            last_name=nombre.split(' ')[1] if ' ' in nombre else '',
            email=f"{username}@clinica.com"
        )
        
        # Crear el paciente
        paciente = Paciente.objects.create(user=user, **validated_data)
        return paciente

    def update(self, instance, validated_data):
        """
        Actualizar paciente - PERMITE actualizar el nombre del usuario
        """
        # Extraer el nombre si viene para actualizar el usuario
        nombre = validated_data.pop('nombre', None)
        
        # Si viene nombre, actualizar el usuario asociado
        if nombre:
            user = instance.user
            user.first_name = nombre.split(' ')[0] if ' ' in nombre else nombre
            user.last_name = nombre.split(' ')[1] if ' ' in nombre else ''
            user.save()
        
        # Validar DNI único (excluyendo el actual)
        dni = validated_data.get('dni')
        if dni and dni != instance.dni:
            if Paciente.objects.filter(dni=dni).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"dni": "Ya existe un paciente con este DNI."})
        
        # Actualizar campos del paciente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Asegurar que los datos se representen correctamente
        """
        representation = super().to_representation(instance)
        # Asegurar que nombre_completo esté siempre presente
        if not representation.get('nombre_completo'):
            representation['nombre_completo'] = self.get_nombre_completo(instance)
        return representation