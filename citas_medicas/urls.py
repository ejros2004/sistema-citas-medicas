# citas_medicas/urls.py - COMPLETO
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render

@ensure_csrf_cookie
def frontend_app(request):
    return render(request, 'frontend/index.html')

@login_required
def app_protegida(request):
    return frontend_app(request)

def home_redirect(request):
    if request.user.is_authenticated:
        print(f"🏠 HomeRedirect: Usuario {request.user.username} autenticado, redirigiendo a /app/")
        return redirect('/app/')
    else:
        print("🏠 HomeRedirect: Usuario no autenticado, redirigiendo a /login/")
        return redirect('/login/')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('admin/', admin.site.urls),
    path('login/', include('autenticacion.urls')),
    path('app/', app_protegida, name='app'),
    path('api/autenticacion/', include('autenticacion.urls_api')),
    path('api/pacientes/', include('pacientes.urls')),
    path('api/medicos/', include('medicos.urls')),
    path('api/citas/', include('citas.urls')),
]