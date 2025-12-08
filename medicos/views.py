# medicos/views.py - MODIFICAR
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import action
from django.db import transaction
import logging
from .models import Medico, Especialidad
from .serializers import MedicoSerializer, EspecialidadSerializer

logger = logging.getLogger(__name__)

# ==================== PERMISOS PERSONALIZADOS ====================

class EsAdmin(BasePermission):
    """Permiso que solo permite acceso a administradores"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'admin'

class PermisoMedicos(BasePermission):
    """Permiso personalizado para operaciones de médicos"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Solo admin puede ver/editar/eliminar médicos
        return hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'admin'

class PermisoEspecialidades(BasePermission):
    """Permiso personalizado para operaciones de especialidades"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Solo admin puede manejar especialidades
        return hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'admin'

# ==================== VIEWSETS ====================

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [IsAuthenticated, PermisoEspecialidades]
    
    def list(self, request, *args, **kwargs):
        try:
            logger.info(f"📋 LIST especialidades solicitado por {request.user.username}")
            especialidades = self.get_queryset()
            serializer = self.get_serializer(especialidades, many=True)
            logger.info(f"✅ Retornando {len(serializer.data)} especialidades")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"❌ Error obteniendo especialidades: {str(e)}")
            return Response(
                {'error': f'Error al obtener especialidades: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all().select_related('user', 'especialidad')
    serializer_class = MedicoSerializer
    permission_classes = [IsAuthenticated, PermisoMedicos]
    
    def list(self, request, *args, **kwargs):
        try:
            logger.info(f"📋 LIST médicos solicitado por {request.user.username}")
            medicos = self.get_queryset()
            serializer = self.get_serializer(medicos, many=True)
            logger.info(f"✅ Retornando {len(serializer.data)} médicos")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"❌ Error obteniendo médicos: {str(e)}")
            return Response(
                {'error': f'Error al obtener médicos: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"➕ CREATE médico solicitado por {request.user.username}")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                medico = serializer.save()
                
                logger.info(f"✅ Médico creado - ID: {medico.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"❌ Error creando médico: {str(e)}")
            return Response(
                {'error': f'Error al crear médico: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )