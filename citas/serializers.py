# citas/serializers.py - REEMPLAZAR
from rest_framework import serializers
from .models import Cita

class CitaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.user.get_full_name', read_only=True)
    medico_nombre = serializers.CharField(source='medico.user.get_full_name', read_only=True)
    paciente_id = serializers.IntegerField(source='paciente.id', read_only=True)
    medico_id = serializers.IntegerField(source='medico.id', read_only=True)
    
    class Meta:
        model = Cita
        fields = [
            'id', 'paciente', 'medico', 'paciente_id', 'medico_id',
            'paciente_nombre', 'medico_nombre', 'fecha', 'hora', 
            'motivo', 'estado'
        ]
        # PACIENTE Y MEDICO DEBEN SER DE ESCRITURA
        read_only_fields = ['id', 'estado', 'paciente_nombre', 'medico_nombre', 'paciente_id', 'medico_id']

    def validate(self, data):
        medico = data.get('medico')
        fecha = data.get('fecha')
        hora = data.get('hora')
        
        if self.instance:
            citas_existentes = Cita.objects.filter(medico=medico, fecha=fecha, hora=hora).exclude(id=self.instance.id)
        else:
            citas_existentes = Cita.objects.filter(medico=medico, fecha=fecha, hora=hora)
        
        if citas_existentes.exists():
            raise serializers.ValidationError("El médico ya tiene una cita programada en ese horario.")
        
        return data