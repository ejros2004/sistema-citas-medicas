# pacientes/views.py - VERSIÓN COMPLETA FINAL
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.db import transaction
import logging
from .models import Paciente
from .serializers import PacienteSerializer

logger = logging.getLogger(__name__)

# ==================== PERMISOS PERSONALIZADOS ====================

class PermisoPacientes(BasePermission):
    """Permiso personalizado para operaciones de pacientes"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin puede ver/editar/eliminar todos los pacientes
        # Paciente solo puede ver su propio perfil
        return hasattr(request.user, 'perfil')
    
    def has_object_permission(self, request, view, obj):
        """Permisos a nivel de objeto"""
        if not request.user.is_authenticated:
            return False
        
        # Admin puede hacer todo
        if request.user.perfil.tipo_usuario == 'admin':
            return True
        
        # Paciente solo puede ver/editar su propio perfil
        if request.user.perfil.tipo_usuario == 'paciente':
            return obj.user == request.user
        
        return False

# ==================== VIEWSET ====================

class PacienteViewSet(viewsets.ModelViewSet):
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated, PermisoPacientes]
    
    def get_queryset(self):
        """Filtrar pacientes según el rol del usuario"""
        user = self.request.user
        
        if not user.is_authenticated:
            return Paciente.objects.none()
        
        # Admin ve todos los pacientes
        if hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'admin':
            return Paciente.objects.all().select_related('user')
        
        # Paciente ve solo su propio perfil
        if hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'paciente':
            try:
                return Paciente.objects.filter(user=user).select_related('user')
            except Paciente.DoesNotExist:
                return Paciente.objects.none()
        
        # Médico no debería ver pacientes directamente desde aquí
        return Paciente.objects.none()
    
    def list(self, request, *args, **kwargs):
        """
        Listar todos los pacientes (solo admin) o solo el propio (paciente)
        """
        try:
            logger.info(f"📋 LIST pacientes solicitado por {request.user.username} ({request.user.perfil.tipo_usuario})")
            
            # Si es paciente, mostrar solo su perfil
            if request.user.perfil.tipo_usuario == 'paciente':
                try:
                    paciente = Paciente.objects.get(user=request.user)
                    serializer = self.get_serializer(paciente)
                    logger.info(f"👤 Paciente viendo su propio perfil - ID: {paciente.id}")
                    # Retornar como array con un solo elemento
                    return Response([serializer.data])
                except Paciente.DoesNotExist:
                    logger.warning(f"⚠️ Paciente {request.user.username} no tiene perfil de paciente")
                    return Response([], status=status.HTTP_200_OK)
            
            # Admin ve todos
            pacientes = self.get_queryset()
            serializer = self.get_serializer(pacientes, many=True)
            logger.info(f"✅ Retornando {len(serializer.data)} pacientes para admin")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pacientes: {str(e)}")
            return Response(
                {'error': f'Error al obtener pacientes: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Obtener un paciente específico
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"❌ Error obteniendo paciente: {str(e)}")
            return Response(
                {'error': f'Error al obtener paciente: {str(e)}'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        """
        Crear paciente con rollback automático en caso de error
        """
        try:
            logger.info(f"➕ CREATE paciente solicitado por {request.user.username}")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
            # Solo admin puede crear pacientes
            if not hasattr(request.user, 'perfil') or request.user.perfil.tipo_usuario != 'admin':
                return Response(
                    {'error': 'Solo los administradores pueden crear pacientes'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            with transaction.atomic():
                # Validar y crear paciente
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                paciente = serializer.save()
                
                logger.info(f"✅ Paciente creado en BD local - ID: {paciente.id}, DNI: {paciente.dni}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"❌ Error creando paciente: {str(e)}")
            return Response(
                {'error': f'Error al crear paciente: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """
        Actualizar paciente con logging detallado
        """
        try:
            instance = self.get_object()
            logger.info(f"✏️ UPDATE paciente {instance.id} solicitado por {request.user.username}")
            
            with transaction.atomic():
                serializer = self.get_serializer(instance, data=request.data, partial=False)
                serializer.is_valid(raise_exception=True)
                paciente = serializer.save()
                
                logger.info(f"✅ Paciente actualizado - ID: {paciente.id}")
                
                return Response(serializer.data)
                
        except Exception as e:
            logger.error(f"❌ Error actualizando paciente: {str(e)}")
            return Response(
                {'error': f'Error al actualizar paciente: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        Eliminar paciente (solo admin)
        """
        try:
            instance = self.get_object()
            logger.info(f"🗑️ DELETE paciente {instance.id} solicitado por {request.user.username}")
            
            # Solo admin puede eliminar pacientes
            if not hasattr(request.user, 'perfil') or request.user.perfil.tipo_usuario != 'admin':
                return Response(
                    {'error': 'Solo los administradores pueden eliminar pacientes'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            with transaction.atomic():
                paciente_id = instance.id
                paciente_dni = instance.dni
                
                # Eliminar localmente
                instance.delete()
                logger.info(f"✅ Paciente eliminado - ID: {paciente_id}, DNI: {paciente_dni}")
                
                return Response(status=status.HTTP_204_NO_CONTENT)
                
        except Exception as e:
            logger.error(f"❌ Error eliminando paciente: {str(e)}")
            return Response(
                {'error': f'Error al eliminar paciente: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )