# citas/serializers.py
from rest_framework import serializers
from .models import Cita
from pacientes.models import Paciente
from medicos.models import Medico

class CitaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.SerializerMethodField()
    medico_nombre = serializers.SerializerMethodField()
    paciente_id = serializers.IntegerField(source='paciente.id', read_only=True)
    medico_id = serializers.IntegerField(source='medico.id', read_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'id', 'paciente', 'medico', 'paciente_id', 'medico_id',
            'paciente_nombre', 'medico_nombre', 'fecha', 'hora', 
            'motivo', 'estado', 'creada_en'
        ]
        read_only_fields = ['id', 'estado', 'paciente_nombre', 'medico_nombre', 
                          'paciente_id', 'medico_id', 'creada_en']

    def get_paciente_nombre(self, obj):
        if obj.paciente and obj.paciente.user:
            return f"{obj.paciente.user.first_name} {obj.paciente.user.last_name}"
        return "Paciente no encontrado"

    def get_medico_nombre(self, obj):
        if obj.medico and obj.medico.user:
            return f"Dr. {obj.medico.user.first_name} {obj.medico.user.last_name}"
        return "Médico no encontrado"

    def validate(self, data):
        # Validar que el médico exista
        medico = data.get('medico')
        if not Medico.objects.filter(id=medico.id).exists():
            raise serializers.ValidationError({"medico": "El médico no existe."})

        # Validar que el paciente exista
        paciente = data.get('paciente')
        if not Paciente.objects.filter(id=paciente.id).exists():
            raise serializers.ValidationError({"paciente": "El paciente no existe."})

        # Validar horario único para el médico
        fecha = data.get('fecha')
        hora = data.get('hora')
        
        if self.instance:
            citas_existentes = Cita.objects.filter(
                medico=medico, 
                fecha=fecha, 
                hora=hora
            ).exclude(id=self.instance.id)
        else:
            citas_existentes = Cita.objects.filter(
                medico=medico, 
                fecha=fecha, 
                hora=hora
            )
        
        if citas_existentes.exists():
            raise serializers.ValidationError(
                "El médico ya tiene una cita programada en ese horario."
            )

        # Validar que la fecha no sea pasada
        from django.utils import timezone
        from datetime import datetime, date
        
        if fecha < date.today():
            raise serializers.ValidationError(
                {"fecha": "No se pueden programar citas en fechas pasadas."}
            )

        return data