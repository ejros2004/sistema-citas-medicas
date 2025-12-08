# citas_medicas/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render

# ==================== VISTAS ====================

@ensure_csrf_cookie
def frontend_app(request):
    """Vista principal que sirve la aplicación frontend"""
    return render(request, 'frontend/index.html')

@login_required
def app_protegida(request):
    """Vista protegida - alias para frontend_app"""
    return frontend_app(request)

def home_redirect(request):
    """
    Vista para la raíz '/'
    Redirige según autenticación
    """
    if request.user.is_authenticated:
        # Usuario autenticado → va a la aplicación
        print(f"🏠 HomeRedirect: Usuario {request.user.username} autenticado, redirigiendo a /app/")
        return redirect('/app/')
    else:
        # Usuario no autenticado → va al login
        print("🏠 HomeRedirect: Usuario no autenticado, redirigiendo a /login/")
        return redirect('/login/')

# ==================== URL PATTERNS ====================

urlpatterns = [
    # Raíz - redirección inteligente
    path('', home_redirect, name='home'),
    
    # Admin Django
    path('admin/', admin.site.urls),
    
    # Login/Logout (vistas HTML)
    path('login/', include('autenticacion.urls')),
    
    # Aplicación principal (PROTEGIDA)
    path('app/', app_protegida, name='app'),
    
    # APIs
    path('api/autenticacion/', include('autenticacion.urls_api')),
    path('api/pacientes/', include('pacientes.urls')),
    path('api/medicos/', include('medicos.urls')),
    path('api/citas/', include('citas.urls')),
]