from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Medico, Especialidad

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id', 'nombre', 'descripcion']

class MedicoSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField(read_only=True)
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)
    
    # Campos para escritura - CORREGIDOS
    nombre_completo = serializers.CharField(write_only=True, required=True)
    especialidad_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Medico
        fields = [
            'id', 'nombre', 'especialidad_nombre', 
            'nombre_completo', 'especialidad_id',
            'telefono', 'horario_inicio', 'horario_fin'
        ]
        read_only_fields = ['id', 'nombre', 'especialidad_nombre']

    def get_nombre(self, obj):
        if obj.user:
            nombre_completo = f"Dr. {obj.user.first_name} {obj.user.last_name}".strip()
            return nombre_completo if nombre_completo else f"Usuario {obj.user.id}"
        return "Usuario no asignado"

    def create(self, validated_data):
        # Extraer datos para el usuario
        nombre_completo = validated_data.pop('nombre_completo')
        especialidad_id = validated_data.pop('especialidad_id')
        
        # Obtener la especialidad
        try:
            especialidad = Especialidad.objects.get(id=especialidad_id)
        except Especialidad.DoesNotExist:
            raise serializers.ValidationError({"especialidad_id": "La especialidad no existe."})
        
        # Crear usuario automáticamente
        username = f"medico_{User.objects.count() + 1}"
        user = User.objects.create_user(
            username=username,
            password='TempPassword123!',
            first_name=nombre_completo.split(' ')[0] if ' ' in nombre_completo else nombre_completo,
            last_name=nombre_completo.split(' ')[1] if ' ' in nombre_completo else '',
            email=f"{username}@clinica.com"
        )
        
        # Crear el médico
        medico = Medico.objects.create(
            user=user,
            especialidad=especialidad,
            telefono=validated_data['telefono'],
            horario_inicio=validated_data['horario_inicio'],
            horario_fin=validated_data['horario_fin']
        )
        return medico

    def update(self, instance, validated_data):
        # Extraer datos para actualización
        nombre_completo = validated_data.pop('nombre_completo', None)
        especialidad_id = validated_data.pop('especialidad_id', None)
        
        # Actualizar nombre del usuario si se proporciona
        if nombre_completo:
            user = instance.user
            user.first_name = nombre_completo.split(' ')[0] if ' ' in nombre_completo else nombre_completo
            user.last_name = nombre_completo.split(' ')[1] if ' ' in nombre_completo else ''
            user.save()
        
        # Actualizar especialidad si se proporciona
        if especialidad_id:
            try:
                especialidad = Especialidad.objects.get(id=especialidad_id)
                instance.especialidad = especialidad
            except Especialidad.DoesNotExist:
                raise serializers.ValidationError({"especialidad_id": "La especialidad no existe."})
        
        # Actualizar otros campos
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.horario_inicio = validated_data.get('horario_inicio', instance.horario_inicio)
        instance.horario_fin = validated_data.get('horario_fin', instance.horario_fin)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Asegurar que el nombre esté presente
        if not representation.get('nombre'):
            representation['nombre'] = self.get_nombre(instance)
        return representation