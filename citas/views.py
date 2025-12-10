from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.db import transaction
import logging
from .models import Cita
from .serializers import CitaSerializer

logger = logging.getLogger(__name__)

class PermisoCitas(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'perfil')
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.perfil.tipo_usuario == 'admin':
            return True
        
        if request.user.perfil.tipo_usuario == 'medico':
            return obj.medico.user == request.user
        
        if request.user.perfil.tipo_usuario == 'paciente':
            return obj.paciente.user == request.user
        
        return False

class CitaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated, PermisoCitas]
    
    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return Cita.objects.none()
        
        queryset = Cita.objects.all().select_related(
            'paciente__user', 
            'medico__user',
            'medico__especialidad'
        )
        
        if user.perfil.tipo_usuario == 'admin':
            return queryset
        
        if user.perfil.tipo_usuario == 'medico':
            try:
                from medicos.models import Medico
                medico = Medico.objects.get(user=user)
                return queryset.filter(medico=medico)
            except Medico.DoesNotExist:
                return Cita.objects.none()
        
        if user.perfil.tipo_usuario == 'paciente':
            try:
                from pacientes.models import Paciente
                paciente = Paciente.objects.get(user=user)
                return queryset.filter(paciente=paciente)
            except Paciente.DoesNotExist:
                return Cita.objects.none()
        
        return Cita.objects.none()
    
    # ==================== ENDPOINTS DE ESTADO ====================
    
    @action(detail=True, methods=['put'])
    def confirmar(self, request, pk=None):
        try:
            cita = self.get_object()
            
            if cita.estado != 'pendiente':
                return Response(
                    {'error': f'La cita ya está {cita.estado}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not (request.user.perfil.tipo_usuario in ['medico', 'admin']):
                return Response(
                    {'error': 'Solo médicos y administradores pueden confirmar citas'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if request.user.perfil.tipo_usuario == 'medico':
                if cita.medico.user != request.user:
                    return Response(
                        {'error': 'Solo puede confirmar sus propias citas'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            cita.estado = 'confirmada'
            cita.save()
            
            logger.info(f"✅ Cita {cita.id} confirmada por {request.user.username}")
            
            return Response({'message': 'Cita confirmada correctamente', 'estado': cita.estado})
            
        except Exception as e:
            logger.error(f"❌ Error confirmando cita: {str(e)}")
            return Response(
                {'error': f'Error al confirmar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['put'])
    def cancelar(self, request, pk=None):
        try:
            cita = self.get_object()
            
            if cita.estado not in ['pendiente', 'confirmada']:
                return Response(
                    {'error': f'No se puede cancelar una cita {cita.estado}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = request.user
            if user.perfil.tipo_usuario == 'paciente':
                if cita.paciente.user != user:
                    return Response(
                        {'error': 'Solo puede cancelar sus propias citas'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif user.perfil.tipo_usuario == 'medico':
                if cita.medico.user != user:
                    return Response(
                        {'error': 'Solo puede cancelar sus propias citas'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            cita.estado = 'cancelada'
            cita.save()
            
            logger.info(f"✅ Cita {cita.id} cancelada por {request.user.username}")
            
            return Response({'message': 'Cita cancelada correctamente', 'estado': cita.estado})
            
        except Exception as e:
            logger.error(f"❌ Error cancelando cita: {str(e)}")
            return Response(
                {'error': f'Error al cancelar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['put'])
    def finalizar(self, request, pk=None):
        try:
            cita = self.get_object()
            
            if cita.estado != 'confirmada':
                return Response(
                    {'error': f'Solo se pueden finalizar citas confirmadas (actual: {cita.estado})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not (request.user.perfil.tipo_usuario in ['medico', 'admin']):
                return Response(
                    {'error': 'Solo médicos y administradores pueden finalizar citas'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if request.user.perfil.tipo_usuario == 'medico':
                if cita.medico.user != request.user:
                    return Response(
                        {'error': 'Solo puede finalizar sus propias citas'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            cita.estado = 'finalizada'
            cita.save()
            
            logger.info(f"✅ Cita {cita.id} finalizada por {request.user.username}")
            
            return Response({'message': 'Cita finalizada correctamente', 'estado': cita.estado})
            
        except Exception as e:
            logger.error(f"❌ Error finalizando cita: {str(e)}")
            return Response(
                {'error': f'Error al finalizar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ==================== CRUD STANDARD ====================
    
    def list(self, request, *args, **kwargs):
        try:
            logger.info(f"📋 LIST citas solicitado por {request.user.username} ({request.user.perfil.tipo_usuario})")
            
            citas = self.get_queryset()
            serializer = self.get_serializer(citas, many=True)
            
            logger.info(f"✅ Retornando {len(serializer.data)} citas para {request.user.perfil.tipo_usuario}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo citas: {str(e)}")
            return Response(
                {'error': f'Error al obtener citas: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"➕ CREATE cita solicitado por {request.user.username}")
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = request.user
            data = request.data.copy()
            
            if user.perfil.tipo_usuario == 'paciente':
                try:
                    from pacientes.models import Paciente
                    paciente = Paciente.objects.get(user=user)
                    data['paciente'] = paciente.id
                    logger.info(f"👤 Paciente auto-asignado: {paciente.id}")
                except Paciente.DoesNotExist:
                    return Response(
                        {'error': 'No se encontró perfil de paciente'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if user.perfil.tipo_usuario == 'medico':
                try:
                    from medicos.models import Medico
                    medico = Medico.objects.get(user=user)
                    data['medico'] = medico.id
                    logger.info(f"👨‍⚕️ Médico auto-asignado: {medico.id}")
                except Medico.DoesNotExist:
                    return Response(
                        {'error': 'No se encontró perfil de médico'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            cita = serializer.save()
            
            logger.info(f"✅ Cita creada - ID: {cita.id}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"❌ Error creando cita: {str(e)}")
            return Response(
                {'error': f'Error al crear cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"✏️ UPDATE cita {instance.id} solicitado por {request.user.username}")
            
            if instance.estado in ['finalizada', 'cancelada']:
                return Response(
                    {'error': f'No se pueden editar citas {instance.estado}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            cita = serializer.save()
            
            logger.info(f"✅ Cita actualizada - ID: {cita.id}")
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error actualizando cita: {str(e)}")
            return Response(
                {'error': f'Error al actualizar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"🗑️ DELETE cita {instance.id} solicitado por {request.user.username}")
            
            if request.user.perfil.tipo_usuario != 'admin':
                return Response(
                    {'error': 'Solo los administradores pueden eliminar citas'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            instance.delete()
            logger.info(f"✅ Cita eliminada - ID: {instance.id}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"❌ Error eliminando cita: {str(e)}")
            return Response(
                {'error': f'Error al eliminar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )