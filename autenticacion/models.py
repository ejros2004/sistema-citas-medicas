# autenticacion/models.py - VERSIÓN CORREGIDA COMPLETA
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
        """Sobreescribir save para asegurar que superusers sean admin"""
        if self.user.is_superuser and self.tipo_usuario != 'admin':
            self.tipo_usuario = 'admin'
        super().save(*args, **kwargs)


# SEÑAL CORREGIDA - VERSIÓN ROBUSTA
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal optimizada para crear/actualizar perfiles de usuario.
    - Si el usuario es superuser, SIEMPRE debe ser admin
    - Si es nuevo, crea el perfil con el tipo correcto
    - Si ya existe, asegura que el tipo sea correcto
    """
    try:
        # Usar get_or_create para evitar problemas de concurrencia
        perfil, perfil_creado = PerfilUsuario.objects.get_or_create(user=instance)
        
        # SI ES SUPERUSER, DEBE SER ADMIN
        if instance.is_superuser:
            if perfil.tipo_usuario != 'admin':
                perfil.tipo_usuario = 'admin'
                perfil.save()
        
        # Si el perfil es nuevo y no es superuser, usar el valor por defecto
        elif perfil_creado and not instance.is_superuser:
            # Ya tiene el valor por defecto 'paciente' del campo
            pass
        
        # Si el usuario ya existe pero el perfil fue creado ahora
        elif created and not instance.is_superuser:
            # Usuario nuevo, no superuser -> paciente
            perfil.tipo_usuario = 'paciente'
            perfil.save()
            
    except Exception as e:
        print(f"❌ Error crítico manejando perfil de {instance.username}: {str(e)}")
        # En caso de error, intentar crear el perfil de emergencia
        try:
            if instance.is_superuser:
                PerfilUsuario.objects.create(user=instance, tipo_usuario='admin')
            else:
                PerfilUsuario.objects.create(user=instance)
        except Exception as emergency_error:
            print(f"🔥 Error de emergencia: No se pudo crear perfil para {instance.username}: {str(emergency_error)}")