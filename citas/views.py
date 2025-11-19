from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.db import transaction
import logging
from .models import Cita
from .serializers import CitaSerializer

logger = logging.getLogger(__name__)

class CitaViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Cita.objects.all().select_related('paciente__user', 'medico__user', 'medico__especialidad')
    serializer_class = CitaSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            logger.info("📋 LIST citas solicitado")
            citas = self.get_queryset()
            serializer = self.get_serializer(citas, many=True)
            logger.info(f"✅ Retornando {len(serializer.data)} citas")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"❌ Error obteniendo citas: {str(e)}")
            return Response(
                {'error': f'Error al obtener citas: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            logger.info("➕ CREATE cita solicitado")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
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
            logger.info(f"✏️ UPDATE cita {instance.id} solicitado")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
            with transaction.atomic():
                # Permitir actualización parcial
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
            logger.info(f"🗑️ DELETE cita {instance.id} solicitado")
            
            with transaction.atomic():
                cita_id = instance.id
                instance.delete()
                logger.info(f"✅ Cita eliminada - ID: {cita_id}")
                
                return Response(status=status.HTTP_204_NO_CONTENT)
                
        except Exception as e:
            logger.error(f"❌ Error eliminando cita: {str(e)}")
            return Response(
                {'error': f'Error al eliminar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'])
    def cancelar(self, request, pk=None):
        try:
            cita = self.get_object()
            logger.info(f"❌ CANCELAR cita {cita.id} solicitado")
            
            if cita.estado == 'cancelada':
                return Response({'error': 'La cita ya está cancelada'}, status=status.HTTP_400_BAD_REQUEST)
            
            cita.estado = 'cancelada'
            cita.save()
            
            # Serializar la respuesta
            serializer = self.get_serializer(cita)
            logger.info(f"✅ Cita cancelada - ID: {cita.id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error cancelando cita: {str(e)}")
            return Response(
                {'error': f'Error al cancelar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'])
    def confirmar(self, request, pk=None):
        try:
            cita = self.get_object()
            logger.info(f"✅ CONFIRMAR cita {cita.id} solicitado")
            
            if cita.estado == 'confirmada':
                return Response({'error': 'La cita ya está confirmada'}, status=status.HTTP_400_BAD_REQUEST)
            
            cita.estado = 'confirmada'
            cita.save()
            
            # Serializar la respuesta
            serializer = self.get_serializer(cita)
            logger.info(f"✅ Cita confirmada - ID: {cita.id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error confirmando cita: {str(e)}")
            return Response(
                {'error': f'Error al confirmar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'])
    def finalizar(self, request, pk=None):
        try:
            cita = self.get_object()
            logger.info(f"🏁 FINALIZAR cita {cita.id} solicitado")
            
            if cita.estado == 'finalizada':
                return Response({'error': 'La cita ya está finalizada'}, status=status.HTTP_400_BAD_REQUEST)
            
            cita.estado = 'finalizada'
            cita.save()
            
            # Serializar la respuesta
            serializer = self.get_serializer(cita)
            logger.info(f"✅ Cita finalizada - ID: {cita.id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"❌ Error finalizando cita: {str(e)}")
            return Response(
                {'error': f'Error al finalizar cita: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )