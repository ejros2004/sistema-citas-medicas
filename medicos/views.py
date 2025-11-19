from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.db import transaction
import logging
from .models import Medico, Especialidad
from .serializers import MedicoSerializer, EspecialidadSerializer

logger = logging.getLogger(__name__)

class EspecialidadViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    
    # ✅ Asegurar que todos los métodos estén permitidos
    def list(self, request, *args, **kwargs):
        try:
            logger.info("📋 LIST especialidades solicitado")
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
    permission_classes = [AllowAny]
    queryset = Medico.objects.all().select_related('user', 'especialidad')
    serializer_class = MedicoSerializer
    
    # ✅ MÉTODO LIST - Para GET /api/medicos/
    def list(self, request, *args, **kwargs):
        try:
            logger.info("📋 LIST médicos solicitado")
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

    # ✅ MÉTODO CREATE - Para POST /api/medicos/
    def create(self, request, *args, **kwargs):
        try:
            logger.info("➕ CREATE médico solicitado")
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

    # ✅ MÉTODO RETRIEVE - Para GET /api/medicos/{id}/
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"❌ Error obteniendo médico: {str(e)}")
            return Response(
                {'error': f'Error al obtener médico: {str(e)}'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    # ✅ MÉTODO UPDATE - Para PUT /api/medicos/{id}/
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"✏️ UPDATE médico {instance.id} solicitado")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
            with transaction.atomic():
                serializer = self.get_serializer(instance, data=request.data, partial=False)
                serializer.is_valid(raise_exception=True)
                medico = serializer.save()
                
                logger.info(f"✅ Médico actualizado - ID: {medico.id}")
                return Response(serializer.data)
                
        except Exception as e:
            logger.error(f"❌ Error actualizando médico: {str(e)}")
            return Response(
                {'error': f'Error al actualizar médico: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # ✅ MÉTODO DESTROY - Para DELETE /api/medicos/{id}/
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"🗑️ DELETE médico {instance.id} solicitado")
            
            with transaction.atomic():
                medico_id = instance.id
                user_id = instance.user.id
                instance.delete()
                
                # Opcional: eliminar el usuario también
                from django.contrib.auth.models import User
                User.objects.filter(id=user_id).delete()
                
                logger.info(f"✅ Médico eliminado - ID: {medico_id}")
                return Response(status=status.HTTP_204_NO_CONTENT)
                
        except Exception as e:
            logger.error(f"❌ Error eliminando médico: {str(e)}")
            return Response(
                {'error': f'Error al eliminar médico: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )