from django.db import models
from django.contrib.auth.models import User

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_medico')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, related_name='medicos')
    telefono = models.CharField(max_length=20)
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.especialidad.nombre if self.especialidad else 'Sin especialidad'}"