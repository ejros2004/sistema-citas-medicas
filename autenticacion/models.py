# autenticacion/models.py - COMPLETO
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
    
    def save(self, *args, **kwargs):
        if self.user.is_superuser and self.tipo_usuario != 'admin':
            self.tipo_usuario = 'admin'
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    try:
        perfil, perfil_creado = PerfilUsuario.objects.get_or_create(user=instance)
        
        if instance.is_superuser:
            if perfil.tipo_usuario != 'admin':
                perfil.tipo_usuario = 'admin'
                perfil.save()
        
        elif perfil_creado and not instance.is_superuser:
            pass
        
        elif created and not instance.is_superuser:
            perfil.tipo_usuario = 'paciente'
            perfil.save()
            
    except Exception as e:
        print(f"❌ Error crítico manejando perfil de {instance.username}: {str(e)}")
        try:
            if instance.is_superuser:
                PerfilUsuario.objects.create(user=instance, tipo_usuario='admin')
            else:
                PerfilUsuario.objects.create(user=instance)
        except Exception as emergency_error:
            print(f"🔥 Error de emergencia: No se pudo crear perfil para {instance.username}: {str(emergency_error)}")