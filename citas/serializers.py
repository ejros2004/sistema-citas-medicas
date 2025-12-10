from rest_framework import serializers
from .models import Cita
from pacientes.models import Paciente
from medicos.models import Medico
from django.utils import timezone
from datetime import datetime, timedelta

class CitaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.SerializerMethodField()
    paciente_dni = serializers.CharField(source='paciente.dni', read_only=True)
    medico_nombre = serializers.SerializerMethodField()
    especialidad_nombre = serializers.CharField(source='medico.especialidad.nombre', read_only=True)
    fecha_str = serializers.SerializerMethodField()
    hora_str = serializers.SerializerMethodField()
    
    class Meta:
        model = Cita
        fields = [
            'id', 'paciente', 'medico', 'fecha', 'hora', 'motivo', 'estado', 
            'paciente_nombre', 'paciente_dni', 'medico_nombre', 'especialidad_nombre',
            'fecha_str', 'hora_str', 'creada_en'
        ]
        read_only_fields = ['id', 'estado', 'creada_en']
    
    def get_paciente_nombre(self, obj):
        if obj.paciente and obj.paciente.user:
            return f"{obj.paciente.user.first_name} {obj.paciente.user.last_name}".strip()
        return "Sin nombre"
    
    def get_medico_nombre(self, obj):
        if obj.medico and obj.medico.user:
            return f"Dr. {obj.medico.user.first_name} {obj.medico.user.last_name}".strip()
        return "Sin médico"
    
    def get_fecha_str(self, obj):
        if obj.fecha:
            return obj.fecha.strftime('%d/%m/%Y')
        return ""
    
    def get_hora_str(self, obj):
        if obj.hora:
            return obj.hora.strftime('%I:%M %p')
        return ""
    
    def validate(self, data):
        fecha_cita = data.get('fecha')
        hora_cita = data.get('hora')
        
        if fecha_cita and hora_cita:
            ahora = timezone.now()
            fecha_hora_cita = timezone.make_aware(
                datetime.combine(fecha_cita, hora_cita)
            )
            
            if fecha_hora_cita < ahora:
                raise serializers.ValidationError({
                    'fecha': 'No se pueden crear citas en el pasado'
                })
            
            medico = data.get('medico')
            if medico:
                try:
                    medico_obj = Medico.objects.get(id=medico.id if hasattr(medico, 'id') else medico)
                    
                    cita_existente = Cita.objects.filter(
                        medico=medico_obj,
                        fecha=fecha_cita,
                        hora=hora_cita,
                        estado__in=['pendiente', 'confirmada']
                    )
                    
                    if self.instance:
                        cita_existente = cita_existente.exclude(id=self.instance.id)
                    
                    if cita_existente.exists():
                        raise serializers.ValidationError({
                            'hora': 'El médico ya tiene una cita programada en este horario'
                        })
                    
                    if hora_cita < medico_obj.horario_inicio or hora_cita > medico_obj.horario_fin:
                        raise serializers.ValidationError({
                            'hora': f'El médico solo atiende de {medico_obj.horario_inicio.strftime("%I:%M %p")} a {medico_obj.horario_fin.strftime("%I:%M %p")}'
                        })
                        
                except Medico.DoesNotExist:
                    raise serializers.ValidationError({
                        'medico': 'El médico especificado no existe'
                    })
        
        return data
    
    def create(self, validated_data):
        validated_data['estado'] = 'pendiente'
        return super().create(validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation