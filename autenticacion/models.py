# autenticacion/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('paciente', 'Paciente'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='paciente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"

# Señal optimizada: Maneja creación y actualización segura
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # Si el usuario es nuevo, creamos el perfil
        PerfilUsuario.objects.create(user=instance)
    else:
        # Si el usuario ya existe, intentamos guardar su perfil
        # Si no tiene perfil (causa de tu error), lo creamos aquí mismo
        try:
            instance.perfil.save()
        except PerfilUsuario.DoesNotExist: # Capturamos el error específico
            PerfilUsuario.objects.create(user=instance, tipo_usuario='admin' if instance.is_superuser else 'paciente')
