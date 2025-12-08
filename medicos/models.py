# medicos/models.py
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

# 1. MODELO ESPECIALIDAD
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# 2. MODELO MEDICO
class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fin = models.TimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        nombre = self.user.username if self.user else 'Sin Usuario'
        especialidad = self.especialidad.nombre if self.especialidad else 'Sin Especialidad'
        return f"Dr/a. {nombre} - {especialidad}"

# 3. SEÑALES
@receiver(post_save, sender=Medico)
def crear_usuario_medico(sender, instance, created, **kwargs):
    """Crear usuario automáticamente cuando se crea un médico sin usuario"""
    
    # Solo ejecutamos si se acaba de crear Y no tiene usuario asignado
    if created and not instance.user:
        # Generar datos base
        username = f"medico_{instance.id}"
        email = f"{username}@clinica.com"
        
        # Valores por defecto
        nombre = "Médico" 
        apellido = f"{instance.id}"
        
        # Crear el usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password='TempPassword123!', 
            first_name=nombre,
            last_name=apellido
        )
        
        # Asignar el usuario creado a la instancia de Médico
        instance.user = user
        
        # Usamos update_fields para evitar un bucle infinito
        instance.save(update_fields=['user'])
        
        # Asegurar que tenga perfil
        from autenticacion.models import PerfilUsuario
        try:
            perfil = user.perfil
            perfil.tipo_usuario = 'medico'
            perfil.save()
        except PerfilUsuario.DoesNotExist:
            PerfilUsuario.objects.create(user=user, tipo_usuario='medico')
        
        # Asignar a grupo
        grupo, created = Group.objects.get_or_create(name='medico')
        user.groups.add(grupo)

@receiver(pre_delete, sender=Medico)
def eliminar_usuario_medico(sender, instance, **kwargs):
    """Eliminar el usuario de autenticación si se borra el médico"""
    if instance.user:
        instance.user.delete()