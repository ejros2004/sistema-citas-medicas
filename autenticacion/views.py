# autenticacion/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import PerfilUsuario
import logging

logger = logging.getLogger(__name__)

# ==================== VISTAS HTML ====================

def login_view(request):
    """Vista para renderizar la página de login"""
    if request.user.is_authenticated:
        # Redirigir según el tipo de usuario
        if hasattr(request.user, 'perfil'):
            return redirect_por_rol(request.user.perfil.tipo_usuario)
        return redirect('/')
    
    return render(request, 'autenticacion/login.html')

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    """Vista principal después del login"""
    return render(request, 'index.html')

# ==================== VISTAS API ====================

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            # Iniciar sesión en Django
            login(request, user)
            
            # Obtener información del perfil
            perfil_data = {}
            if hasattr(user, 'perfil'):
                perfil_data = {
                    'tipo_usuario': user.perfil.tipo_usuario,
                    'perfil_id': user.perfil.id
                }
            
            return Response({
                'user': UserSerializer(user).data,
                'perfil': perfil_data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'message': 'Login exitoso'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)

class RegistroAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Iniciar sesión automáticamente
            login(request, user)
            
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CambioPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CambioPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Verificar contraseña actual
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Contraseña actual incorrecta']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cambiar contraseña
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Actualizar sesión para no cerrarla
            update_session_auth_hash(request, user)
            
            return Response({'message': 'Contraseña cambiada exitosamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==================== VISTAS PARA ADMIN ====================

class UserListAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserAdminAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Actualizar tipo de usuario si se envió
            tipo_usuario = request.data.get('tipo_usuario')
            if tipo_usuario and hasattr(user, 'perfil'):
                user.perfil.tipo_usuario = tipo_usuario
                user.perfil.save()
                
                # Actualizar grupos
                user.groups.clear()
                grupo, created = Group.objects.get_or_create(name=tipo_usuario)
                user.groups.add(grupo)
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            
            # No permitir eliminar al superuser actual
            if user == request.user:
                return Response(
                    {'error': 'No puedes eliminar tu propio usuario'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.delete()
            return Response({'message': 'Usuario eliminado exitosamente'})
        
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ==================== FUNCIONES DE AYUDA ====================

def redirect_por_rol(tipo_usuario):
    """Redirige según el tipo de usuario"""
    if tipo_usuario == 'admin':
        return redirect('/')
    elif tipo_usuario == 'medico':
        return redirect('/?tab=citas')
    elif tipo_usuario == 'paciente':
        return redirect('/?tab=citas')
    else:
        return redirect('/')

def es_admin(user):
    """Verifica si el usuario es administrador"""
    return hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'admin'

def es_medico(user):
    """Verifica si el usuario es médico"""
    return hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'medico'

def es_paciente(user):
    """Verifica si el usuario es paciente"""
    return hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'paciente'

# Decoradores personalizados
def admin_required(view_func):
    """Decorador para vistas que requieren ser admin"""
    decorated_view_func = user_passes_test(
        lambda u: es_admin(u) and u.is_authenticated,
        login_url='/login/'
    )(view_func)
    return decorated_view_func

def medico_required(view_func):
    """Decorador para vistas que requieren ser médico"""
    decorated_view_func = user_passes_test(
        lambda u: es_medico(u) and u.is_authenticated,
        login_url='/login/'
    )(view_func)
    return decorated_view_func

def paciente_required(view_func):
    """Decorador para vistas que requieren ser paciente"""
    decorated_view_func = user_passes_test(
        lambda u: es_paciente(u) and u.is_authenticated,
        login_url='/login/'
    )(view_func)
    return decorated_view_func

# Vista para verificar autenticación y rol
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_autenticacion(request):
    """Verifica si el usuario está autenticado y devuelve su información"""
    user = request.user
    perfil_data = {}
    
    if hasattr(user, 'perfil'):
        perfil_data = PerfilUsuarioSerializer(user.perfil).data
    
    return Response({
        'autenticado': True,
        'user': UserSerializer(user).data,
        'perfil': perfil_data
    })