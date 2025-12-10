from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Medico, Especialidad
import re

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id', 'nombre', 'descripcion']

class MedicoSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField(read_only=True)
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    nombre_completo = serializers.CharField(write_only=True, required=True)
    especialidad_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Medico
        fields = [
            'id', 'nombre', 'especialidad_nombre', 
            'nombre_completo', 'especialidad_id',
            'telefono', 'horario_inicio', 'horario_fin',
            'password', 'confirm_password'
        ]
        read_only_fields = ['id', 'nombre', 'especialidad_nombre']

    def get_nombre(self, obj):
        if obj.user:
            nombre_completo = f"Dr. {obj.user.first_name} {obj.user.last_name}".strip()
            return nombre_completo if nombre_completo else f"Usuario {obj.user.id}"
        return "Usuario no asignado"

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        nombre_completo = validated_data.pop('nombre_completo')
        especialidad_id = validated_data.pop('especialidad_id')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        
        try:
            especialidad = Especialidad.objects.get(id=especialidad_id)
        except Especialidad.DoesNotExist:
            raise serializers.ValidationError({"especialidad_id": "La especialidad no existe."})
        
        nombres = nombre_completo.split(' ')
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
            first_name=nombre_completo.split(' ')[0] if ' ' in nombre_completo else nombre_completo,
            last_name=nombre_completo.split(' ')[1] if ' ' in nombre_completo else '',
            email=f"{username}@clinica.com"
        )
        
        medico = Medico.objects.create(
            user=user,
            especialidad=especialidad,
            telefono=validated_data['telefono'],
            horario_inicio=validated_data['horario_inicio'],
            horario_fin=validated_data['horario_fin']
        )
        
        from autenticacion.models import PerfilUsuario
        if hasattr(user, 'perfil'):
            user.perfil.tipo_usuario = 'medico'
            user.perfil.save()
        
        return medico

    def update(self, instance, validated_data):
        nombre_completo = validated_data.pop('nombre_completo', None)
        especialidad_id = validated_data.pop('especialidad_id', None)
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)
        
        if password:
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
            user = instance.user
            user.set_password(password)
            user.save()
        
        if nombre_completo:
            user = instance.user
            user.first_name = nombre_completo.split(' ')[0] if ' ' in nombre_completo else nombre_completo
            user.last_name = nombre_completo.split(' ')[1] if ' ' in nombre_completo else ''
            user.save()
        
        if especialidad_id:
            try:
                especialidad = Especialidad.objects.get(id=especialidad_id)
                instance.especialidad = especialidad
            except Especialidad.DoesNotExist:
                raise serializers.ValidationError({"especialidad_id": "La especialidad no existe."})
        
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.horario_inicio = validated_data.get('horario_inicio', instance.horario_inicio)
        instance.horario_fin = validated_data.get('horario_fin', instance.horario_fin)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation.get('nombre'):
            representation['nombre'] = self.get_nombre(instance)
        return representation