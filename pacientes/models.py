from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

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

@receiver(post_save, sender=Paciente)
def crear_usuario_paciente(sender, instance, created, **kwargs):
    """Crear usuario automáticamente cuando se crea un paciente sin usuario"""
    
    if created and not instance.user:
        username = f"paciente_{instance.dni}"
        username = username.replace(' ', '').replace('-', '') 
        email = f"{username}@clinica.com"
        
        nombre = "Paciente"
        apellido = f"{instance.dni}"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='TempPassword123!',
            first_name=nombre,
            last_name=apellido
        )
        
        instance.user = user
        instance.save(update_fields=['user'])
        
        from autenticacion.models import PerfilUsuario
        try:
            perfil = user.perfil
            perfil.tipo_usuario = 'paciente'
            perfil.save()
        except PerfilUsuario.DoesNotExist:
            PerfilUsuario.objects.create(user=user, tipo_usuario='paciente')
        
        grupo, created = Group.objects.get_or_create(name='paciente')
        user.groups.add(grupo)

@receiver(pre_delete, sender=Paciente)
def eliminar_usuario_paciente(sender, instance, **kwargs):
    """Eliminar usuario cuando se elimina un paciente"""
    if instance.user:
        instance.user.delete()