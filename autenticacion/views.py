# autenticacion/views.py - COMPLETO CON CORRECCIÓN CRÍTICA
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
    print(f"🔐 LoginView HTML accedida por: {request.user} - Autenticado: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        print(f"✅ Usuario ya autenticado ({request.user.username}), redirigiendo a /app/")
        return redirect('/app/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"📝 Intento de login HTML: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            print(f"✅ Login HTML exitoso para {username}")
            
            return redirect('/app/')
        else:
            print(f"❌ Credenciales inválidas para {username}")
            return render(request, 'autenticacion/login.html', {
                'error': 'Credenciales inválidas. Intenta nuevamente.'
            })
    
    return render(request, 'autenticacion/login.html')

def logout_view(request):
    print(f"👋 Logout de {request.user.username}")
    logout(request)
    return redirect('/login/')

@login_required
def dashboard_view(request):
    return render(request, 'index.html')

# ==================== VISTAS API ====================

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            if user.is_superuser:
                perfil, created = PerfilUsuario.objects.get_or_create(user=user)
                if perfil.tipo_usuario != 'admin':
                    perfil.tipo_usuario = 'admin'
                    perfil.save()
                    logger.info(f"✅ Superuser {user.username} configurado como admin")
            
            refresh = RefreshToken.for_user(user)
            
            login(request, user)
            
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
            
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Contraseña actual incorrecta']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
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
            
            tipo_usuario = request.data.get('tipo_usuario')
            if tipo_usuario and hasattr(user, 'perfil'):
                user.perfil.tipo_usuario = tipo_usuario
                user.perfil.save()
                
                user.groups.clear()
                grupo, created = Group.objects.get_or_create(name=tipo_usuario)
                user.groups.add(grupo)
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            
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
    if tipo_usuario == 'admin':
        return redirect('/')
    elif tipo_usuario == 'medico':
        return redirect('/?tab=citas')
    elif tipo_usuario == 'paciente':
        return redirect('/?tab=citas')
    else:
        return redirect('/')

def es_admin(user):
    return hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'admin'

def es_medico(user):
    return hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'medico'

def es_paciente(user):
    return hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'paciente'

def admin_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: es_admin(u) and u.is_authenticated,
        login_url='/login/'
    )(view_func)
    return decorated_view_func

def medico_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: es_medico(u) and u.is_authenticated,
        login_url='/login/'
    )(view_func)
    return decorated_view_func

def paciente_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: es_paciente(u) and u.is_authenticated,
        login_url='/login/'
    )(view_func)
    return decorated_view_func

# ==================== VISTA CORREGIDA - ¡ESTA ES LA CLAVE! ====================

@api_view(['GET'])
@permission_classes([AllowAny])  # ¡CAMBIADO de [IsAuthenticated] a [AllowAny]!
def verificar_autenticacion(request):
    """Verifica si el usuario está autenticado y devuelve su información"""
    user = request.user
    
    # Si no está autenticado, devolver información básica
    if not user.is_authenticated:
        return Response({
            'autenticado': False,
            'message': 'Usuario no autenticado'
        })
    
    # Si es superuser, asegurar que sea admin
    if user.is_superuser:
        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        if perfil.tipo_usuario != 'admin':
            perfil.tipo_usuario = 'admin'
            perfil.save()
            logger.info(f"✅ Superuser {user.username} corregido a admin en verificación")
    
    perfil_data = {}
    if hasattr(user, 'perfil'):
        perfil_data = PerfilUsuarioSerializer(user.perfil).data
    
    return Response({
        'autenticado': True,
        'user': UserSerializer(user).data,
        'perfil': perfil_data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_info(request):
    from django.contrib.auth.models import User
    from pacientes.models import Paciente
    from medicos.models import Medico
    from citas.models import Cita
    
    info = {
        'request_user': request.user.username if request.user.is_authenticated else 'No autenticado',
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
        'total_users': User.objects.count(),
        'total_pacientes': Paciente.objects.count(),
        'total_medicos': Medico.objects.count(),
        'total_citas': Cita.objects.count(),
    }
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil'):
            info['perfil'] = {
                'tipo_usuario': request.user.perfil.tipo_usuario,
                'perfil_id': request.user.perfil.id,
                'telefono': request.user.perfil.telefono,
            }
        
        if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'paciente':
            try:
                paciente = Paciente.objects.get(user=request.user)
                info['paciente_info'] = {
                    'id': paciente.id,
                    'dni': paciente.dni,
                    'has_citas': Cita.objects.filter(paciente=paciente).exists(),
                    'citas_count': Cita.objects.filter(paciente=paciente).count(),
                }
            except Paciente.DoesNotExist:
                info['paciente_info'] = 'ERROR: No tiene objeto Paciente'
        
        if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'medico':
            try:
                medico = Medico.objects.get(user=request.user)
                info['medico_info'] = {
                    'id': medico.id,
                    'especialidad': medico.especialidad.nombre if medico.especialidad else 'Sin especialidad',
                    'has_citas': Cita.objects.filter(medico=medico).exists(),
                    'citas_count': Cita.objects.filter(medico=medico).count(),
                }
            except Medico.DoesNotExist:
                info['medico_info'] = 'ERROR: No tiene objeto Medico'
    
    return Response(info)