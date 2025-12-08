# pacientes/models.py
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

# 1. MODELO PACIENTE
class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True, null=True) 
    actualizado_en = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.dni} - {self.user.username if self.user else 'Sin Usuario'}"

# 2. SEÑALES
@receiver(post_save, sender=Paciente)
def crear_usuario_paciente(sender, instance, created, **kwargs):
    """Crear usuario automáticamente cuando se crea un paciente sin usuario"""
    
    # Verificamos si es nuevo Y si no tiene usuario asignado
    if created and not instance.user:
        # Generar username basado en el DNI
        username = f"paciente_{instance.dni}"
        # Limpiar posibles caracteres extraños
        username = username.replace(' ', '').replace('-', '') 
        email = f"{username}@clinica.com"
        
        # Valores por defecto
        nombre = "Paciente"
        apellido = f"{instance.dni}"
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password='TempPassword123!',
            first_name=nombre,
            last_name=apellido
        )
        
        # Asignar al paciente
        instance.user = user
        instance.save(update_fields=['user'])
        
        # Asegurar que tenga perfil
        from autenticacion.models import PerfilUsuario
        try:
            perfil = user.perfil
            perfil.tipo_usuario = 'paciente'
            perfil.save()
        except PerfilUsuario.DoesNotExist:
            PerfilUsuario.objects.create(user=user, tipo_usuario='paciente')
        
        # Asignar a grupo
        grupo, created = Group.objects.get_or_create(name='paciente')
        user.groups.add(grupo)

@receiver(pre_delete, sender=Paciente)
def eliminar_usuario_paciente(sender, instance, **kwargs):
    """Eliminar usuario cuando se elimina un paciente"""
    if instance.user:
        instance.user.delete()