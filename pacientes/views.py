from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Paciente
from .serializers import PacienteSerializer
from django.db import transaction
import requests
import os
import logging

logger = logging.getLogger(__name__)

class PacienteViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Paciente.objects.all().select_related('user')
    serializer_class = PacienteSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Listar todos los pacientes
        """
        try:
            logger.info("📋 LIST pacientes solicitado")
            pacientes = self.get_queryset()
            serializer = self.get_serializer(pacientes, many=True)
            logger.info(f"✅ Retornando {len(serializer.data)} pacientes")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"❌ Error obteniendo pacientes: {str(e)}")
            return Response(
                {'error': f'Error al obtener pacientes: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """
        Crear paciente con rollback automático en caso de error
        """
        try:
            logger.info("➕ CREATE paciente solicitado")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
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
            logger.info(f"✏️ UPDATE paciente {instance.id} solicitado")
            logger.info(f"📦 Datos antes: DNI={instance.dni}, Tel={instance.telefono}, Dir={instance.direccion}")
            logger.info(f"📦 Datos recibidos: {request.data}")
            
            with transaction.atomic():
                serializer = self.get_serializer(instance, data=request.data, partial=False)
                serializer.is_valid(raise_exception=True)
                paciente = serializer.save()
                
                # Refrescar desde BD para ver cambios reales
                paciente.refresh_from_db()
                logger.info(f"✅ Paciente actualizado - ID: {paciente.id}")
                logger.info(f"📦 Datos después: DNI={paciente.dni}, Tel={paciente.telefono}, Dir={paciente.direccion}")
                
                # Si se cambió el nombre, mostrar info del usuario
                if 'nombre' in request.data:
                    logger.info(f"👤 Usuario actualizado: {paciente.user.first_name} {paciente.user.last_name}")
                
                return Response(serializer.data)
                
        except Exception as e:
            logger.error(f"❌ Error actualizando paciente: {str(e)}")
            return Response(
                {'error': f'Error al actualizar paciente: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        Eliminar paciente
        """
        try:
            instance = self.get_object()
            logger.info(f"🗑️ DELETE paciente {instance.id} solicitado")
            
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