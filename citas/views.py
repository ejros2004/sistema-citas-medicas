# citas/views.py - VERSIÓN COMPLETA CORREGIDA
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import logging
from .models import Cita
from pacientes.models import Paciente
from medicos.models import Medico
from .serializers import CitaSerializer

logger = logging.getLogger(__name__)

# ==================== PERMISOS PERSONALIZADOS ====================

class PermisoCitas(permissions.BasePermission):
    """Permiso personalizado para operaciones de citas"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'perfil'):
            logger.warning(f"Usuario {request.user.username} no tiene perfil")
            return False
        
        logger.info(f"🔐 PermisoCitas para {request.user.username} ({request.user.perfil.tipo_usuario}) en acción: {view.action}")
        
        # Todos los autenticados pueden listar y ver detalle
        if view.action in ['list', 'retrieve', 'metadata']:
            return True
        
        # Admin puede hacer todo
        if request.user.perfil.tipo_usuario == 'admin':
            return True
        
        # Pacientes pueden crear citas
        if view.action == 'create' and request.user.perfil.tipo_usuario == 'paciente':
            return True
        
        # Médicos pueden confirmar, cancelar, finalizar, actualizar
        if view.action in ['confirmar', 'cancelar', 'finalizar', 'update', 'partial_update']:
            return request.user.perfil.tipo_usuario == 'medico' or request.user.perfil.tipo_usuario == 'admin'
        
        # Admin solo puede eliminar
        if view.action == 'destroy':
            return request.user.perfil.tipo_usuario == 'admin'
        
        # Para acciones personalizadas
        if view.action in ['cancelar', 'confirmar', 'finalizar']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Permisos a nivel de objeto"""
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'perfil'):
            return False
        
        logger.info(f"🔐 Permiso objeto para {request.user.username} en cita {obj.id}")
        
        # Admin puede hacer todo
        if request.user.perfil.tipo_usuario == 'admin':
            return True
        
        # Médico solo puede manejar sus propias citas
        if request.user.perfil.tipo_usuario == 'medico':
            try:
                medico_usuario = Medico.objects.get(user=request.user)
                is_owner = obj.medico == medico_usuario
                logger.info(f"👨‍⚕️ Médico {medico_usuario.id} es dueño de cita {obj.id}? {is_owner}")
                return is_owner
            except Medico.DoesNotExist:
                logger.warning(f"⚠️ Usuario {request.user.username} es médico pero no tiene objeto Medico")
                return False
        
        # Paciente solo puede ver y cancelar sus propias citas
        if request.user.perfil.tipo_usuario == 'paciente':
            try:
                paciente_usuario = Paciente.objects.get(user=request.user)
                is_owner = obj.paciente == paciente_usuario
                logger.info(f"👤 Paciente {paciente_usuario.id} es dueño de cita {obj.id}? {is_owner}")
                
                if view.action == 'destroy':
                    return False  # Paciente no puede eliminar
                if view.action == 'cancelar':
                    # Paciente solo puede cancelar citas pendientes o confirmadas
                    can_cancel = is_owner and obj.estado in ['pendiente', 'confirmada']
                    logger.info(f"👤 Paciente puede cancelar cita {obj.id}? {can_cancel}")
                    return can_cancel
                return is_owner
            except Paciente.DoesNotExist:
                logger.warning(f"⚠️ Usuario {request.user.username} es paciente pero no tiene objeto Paciente")
                return False
        
        return False

# ==================== VIEWSET DE CITAS ====================

class CitaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated, PermisoCitas]
    
    def get_queryset(self):
        """Filtrar citas según el rol del usuario"""
        user = self.request.user
        
        if not user.is_authenticated:
            return Cita.objects.none()
        
        if not hasattr(user, 'perfil'):
            logger.warning(f"⚠️ Usuario {user.username} no tiene perfil")
            return Cita.objects.none()
        
        logger.info(f"📋 Obteniendo queryset para {user.username} ({user.perfil.tipo_usuario})")
        
        # Admin ve todas las citas
        if user.perfil.tipo_usuario == 'admin':
            queryset = Cita.objects.all().select_related(
                'paciente__user', 
                'medico__user', 
                'medico__especialidad'
            )
            logger.info(f"👑 Admin viendo TODAS las citas: {queryset.count()}")
            return queryset
        
        # Médico ve solo sus citas
        if user.perfil.tipo_usuario == 'medico':
            try:
                medico_usuario = Medico.objects.get(user=user)
                queryset = Cita.objects.filter(
                    medico=medico_usuario
                ).select_related(
                    'paciente__user', 
                    'medico__user', 
                    'medico__especialidad'
                )
                logger.info(f"👨‍⚕️ Médico {medico_usuario.id} viendo SUS citas: {queryset.count()}")
                return queryset
            except Medico.DoesNotExist:
                logger.error(f"❌ Usuario {user.username} es médico pero no tiene objeto Medico")
                return Cita.objects.none()
        
        # Paciente ve solo sus citas
        if user.perfil.tipo_usuario == 'paciente':
            try:
                paciente_usuario = Paciente.objects.get(user=user)
                queryset = Cita.objects.filter(
                    paciente=paciente_usuario
                ).select_related(
                    'paciente__user', 
                    'medico__user', 
                    'medico__especialidad'
                )
                logger.info(f"👤 Paciente {paciente_usuario.id} viendo SUS citas: {queryset.count()}")
                return queryset
            except Paciente.DoesNotExist:
                logger.error(f"❌ Usuario {user.username} es paciente pero no tiene objeto Paciente")
                return Cita.objects.none()
        
        logger.warning(f"⚠️ Usuario {user.username} tiene tipo_usuario desconocido: {user.perfil.tipo_usuario}")
        return Cita.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            logger.info(f"📋 LIST citas solicitado por {user.username} ({user.perfil.tipo_usuario})")
            
            queryset = self.get_queryset()
            logger.info(f"📊 Total citas en queryset: {queryset.count()}")
            
            # DEBUG: Mostrar primeras citas
            if queryset.count() > 0:
                for i, cita in enumerate(queryset[:3]):
                    logger.info(f"  Cita {i+1}: ID={cita.id}, Paciente={cita.paciente.dni}, Médico={cita.medico.user.username}, Estado={cita.estado}")
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"✅ Retornando {len(serializer.data)} citas para {user.perfil.tipo_usuario}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"❌ Error obteniendo citas: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al obtener citas: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            logger.info(f"➕ CREATE cita solicitado por {user.username}")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
            # Verificar que sea paciente
            if user.perfil.tipo_usuario != 'paciente':
                logger.warning(f"⛔ Usuario {user.username} ({user.perfil.tipo_usuario}) intentando crear cita sin ser paciente")
                return Response(
                    {'error': 'Solo los pacientes pueden crear citas'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener el paciente asociado al usuario
            try:
                paciente = Paciente.objects.get(user=user)
                logger.info(f"👤 Paciente encontrado: {paciente.id} - {paciente.dni}")
            except Paciente.DoesNotExist:
                logger.error(f"❌ No se encontró paciente para usuario {user.username}")
                return Response(
                    {'error': 'No se encontró perfil de paciente. Contacte al administrador.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear copia de los datos y asignar paciente automáticamente
            cita_data = request.data.copy()
            cita_data['paciente'] = paciente.id
            cita_data['estado'] = 'pendiente'  # Estado por defecto
            
            logger.info(f"📝 Datos procesados: {cita_data}")
            
            with transaction.atomic():
                serializer = self.get_serializer(data=cita_data)
                serializer.is_valid(raise_exception=True)
                cita = serializer.save()
                
                logger.info(f"✅ Cita creada exitosamente - ID: {cita.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"❌ Error creando cita: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al crear cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = request.user
            logger.info(f"✏️ UPDATE cita {instance.id} solicitado por {user.username} ({user.perfil.tipo_usuario})")
            
            # Solo médicos y admin pueden actualizar citas
            if user.perfil.tipo_usuario not in ['medico', 'admin']:
                logger.warning(f"⛔ Usuario {user.username} ({user.perfil.tipo_usuario}) intentando actualizar cita sin permiso")
                return Response(
                    {'error': 'Solo médicos y administradores pueden actualizar citas'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Si es médico, verificar que sea el dueño de la cita
            if user.perfil.tipo_usuario == 'medico':
                try:
                    medico_usuario = Medico.objects.get(user=user)
                    if instance.medico != medico_usuario:
                        logger.warning(f"⛔ Médico {medico_usuario.id} intentando actualizar cita {instance.id} que no es suya")
                        return Response(
                            {'error': 'No tienes permiso para actualizar esta cita'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Medico.DoesNotExist:
                    logger.error(f"❌ Usuario {user.username} es médico pero no tiene objeto Medico")
                    return Response(
                        {'error': 'No se encontró perfil de médico'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            with transaction.atomic():
                # Solo permitir actualización de estado y motivo
                data_permisible = {}
                if 'estado' in request.data:
                    data_permisible['estado'] = request.data['estado']
                if 'motivo' in request.data:
                    data_permisible['motivo'] = request.data['motivo']
                
                serializer = self.get_serializer(instance, data=data_permisible, partial=True)
                serializer.is_valid(raise_exception=True)
                cita = serializer.save()
                
                logger.info(f"✅ Cita actualizada - ID: {cita.id}")
                return Response(serializer.data)
                
        except Exception as e:
            logger.error(f"❌ Error actualizando cita: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al actualizar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user = request.user
            logger.info(f"🗑️ DELETE cita {instance.id} solicitado por {user.username} ({user.perfil.tipo_usuario})")
            
            # Solo admin puede eliminar citas
            if user.perfil.tipo_usuario != 'admin':
                logger.warning(f"⛔ Usuario {user.username} ({user.perfil.tipo_usuario}) intentando eliminar cita sin ser admin")
                return Response(
                    {'error': 'Solo los administradores pueden eliminar citas'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            with transaction.atomic():
                cita_id = instance.id
                instance.delete()
                logger.info(f"✅ Cita eliminada - ID: {cita_id}")
                
                return Response(status=status.HTTP_204_NO_CONTENT)
                
        except Exception as e:
            logger.error(f"❌ Error eliminando cita: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al eliminar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'])
    def cancelar(self, request, pk=None):
        try:
            cita = self.get_object()
            user = request.user
            logger.info(f"❌ CANCELAR cita {cita.id} solicitado por {user.username} ({user.perfil.tipo_usuario})")
            
            # Verificar que el usuario tenga permiso
            if user.perfil.tipo_usuario == 'paciente':
                # Paciente solo puede cancelar sus propias citas
                try:
                    paciente_usuario = Paciente.objects.get(user=user)
                    if cita.paciente != paciente_usuario:
                        logger.warning(f"⛔ Paciente {paciente_usuario.id} intentando cancelar cita {cita.id} que no es suya")
                        return Response(
                            {'error': 'No puedes cancelar citas de otros pacientes'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Paciente.DoesNotExist:
                    logger.error(f"❌ Usuario {user.username} es paciente pero no tiene objeto Paciente")
                    return Response(
                        {'error': 'No se encontró perfil de paciente'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif user.perfil.tipo_usuario == 'medico':
                # Médico solo puede cancelar sus citas
                try:
                    medico_usuario = Medico.objects.get(user=user)
                    if cita.medico != medico_usuario:
                        logger.warning(f"⛔ Médico {medico_usuario.id} intentando cancelar cita {cita.id} que no es suya")
                        return Response(
                            {'error': 'No puedes cancelar citas de otros médicos'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Medico.DoesNotExist:
                    logger.error(f"❌ Usuario {user.username} es médico pero no tiene objeto Medico")
                    return Response(
                        {'error': 'No se encontró perfil de médico'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif user.perfil.tipo_usuario != 'admin':
                logger.warning(f"⛔ Usuario {user.username} ({user.perfil.tipo_usuario}) intentando cancelar cita sin permiso")
                return Response(
                    {'error': 'No tienes permiso para cancelar citas'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validar estado
            if cita.estado == 'cancelada':
                return Response({'error': 'La cita ya está cancelada'}, status=status.HTTP_400_BAD_REQUEST)
            
            if cita.estado == 'finalizada':
                return Response({'error': 'No se puede cancelar una cita finalizada'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Cancelar cita
            cita.estado = 'cancelada'
            cita.save()
            
            serializer = self.get_serializer(cita)
            logger.info(f"✅ Cita cancelada exitosamente - ID: {cita.id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error cancelando cita: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al cancelar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'])
    def confirmar(self, request, pk=None):
        try:
            cita = self.get_object()
            user = request.user
            logger.info(f"✅ CONFIRMAR cita {cita.id} solicitado por {user.username} ({user.perfil.tipo_usuario})")
            
            # Solo médicos y admin pueden confirmar citas
            if user.perfil.tipo_usuario not in ['medico', 'admin']:
                logger.warning(f"⛔ Usuario {user.username} ({user.perfil.tipo_usuario}) intentando confirmar cita sin permiso")
                return Response(
                    {'error': 'Solo médicos y administradores pueden confirmar citas'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Si es médico, verificar que sea su cita
            if user.perfil.tipo_usuario == 'medico':
                try:
                    medico_usuario = Medico.objects.get(user=user)
                    if cita.medico != medico_usuario:
                        logger.warning(f"⛔ Médico {medico_usuario.id} intentando confirmar cita {cita.id} que no es suya")
                        return Response(
                            {'error': 'No puedes confirmar citas de otros médicos'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Medico.DoesNotExist:
                    logger.error(f"❌ Usuario {user.username} es médico pero no tiene objeto Medico")
                    return Response(
                        {'error': 'No se encontró perfil de médico'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Validar estado
            if cita.estado == 'confirmada':
                return Response({'error': 'La cita ya está confirmada'}, status=status.HTTP_400_BAD_REQUEST)
            
            if cita.estado != 'pendiente':
                return Response({'error': 'Solo se pueden confirmar citas pendientes'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Confirmar cita
            cita.estado = 'confirmada'
            cita.save()
            
            serializer = self.get_serializer(cita)
            logger.info(f"✅ Cita confirmada exitosamente - ID: {cita.id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error confirmando cita: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al confirmar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'])
    def finalizar(self, request, pk=None):
        try:
            cita = self.get_object()
            user = request.user
            logger.info(f"🏁 FINALIZAR cita {cita.id} solicitado por {user.username} ({user.perfil.tipo_usuario})")
            
            # Solo médicos y admin pueden finalizar citas
            if user.perfil.tipo_usuario not in ['medico', 'admin']:
                logger.warning(f"⛔ Usuario {user.username} ({user.perfil.tipo_usuario}) intentando finalizar cita sin permiso")
                return Response(
                    {'error': 'Solo médicos y administradores pueden finalizar citas'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Si es médico, verificar que sea su cita
            if user.perfil.tipo_usuario == 'medico':
                try:
                    medico_usuario = Medico.objects.get(user=user)
                    if cita.medico != medico_usuario:
                        logger.warning(f"⛔ Médico {medico_usuario.id} intentando finalizar cita {cita.id} que no es suya")
                        return Response(
                            {'error': 'No puedes finalizar citas de otros médicos'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Medico.DoesNotExist:
                    logger.error(f"❌ Usuario {user.username} es médico pero no tiene objeto Medico")
                    return Response(
                        {'error': 'No se encontró perfil de médico'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Validar estado
            if cita.estado == 'finalizada':
                return Response({'error': 'La cita ya está finalizada'}, status=status.HTTP_400_BAD_REQUEST)
            
            if cita.estado != 'confirmada':
                return Response({'error': 'Solo se pueden finalizar citas confirmadas'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Finalizar cita
            cita.estado = 'finalizada'
            cita.save()
            
            serializer = self.get_serializer(cita)
            logger.info(f"✅ Cita finalizada exitosamente - ID: {cita.id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error finalizando cita: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al finalizar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )