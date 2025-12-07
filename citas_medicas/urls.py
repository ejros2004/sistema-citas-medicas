# citas_medicas/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from . import views

# Vista protegida (mantenemos tu lógica)
@login_required
def app_protegida(request):
    return views.frontend_app(request)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- CAMBIO CLAVE AQUÍ ---
    # Incluimos autenticacion.urls en la raíz (''). 
    # Como ya definimos las rutas completas dentro de ese archivo (ej: 'login/' y 'api/autenticacion/login/'),
    # esto funcionará perfectamente para ambos casos.
    path('', include('autenticacion.urls')),
    
    # Redirección base
    path('', lambda request: redirect('login')),
    
    path('app/', app_protegida, name='frontend_app'),
    
    # Otras APIs
    path('api/pacientes/', include('pacientes.urls')),
    path('api/medicos/', include('medicos.urls')),
    path('api/citas/', include('citas.urls')),
    
]