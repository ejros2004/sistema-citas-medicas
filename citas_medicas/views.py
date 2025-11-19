from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def frontend_app(request):
    """
    Vista principal que sirve la aplicación frontend
    """
    return render(request, 'frontend/index.html')

def api_home(request):
    """
    Vista para la página principal de la API
    """
    return JsonResponse({
        'message': 'Sistema de Citas Médicas - API Django',
        'endpoints': {
            'admin': '/admin/',
            'frontend': '/app/',
            'api_pacientes': '/api/pacientes/',
            'api_medicos': '/api/medicos/',
            'api_citas': '/api/citas/',
            'api_gateway': 'http://localhost:8000/'
        },
        'documentation': 'Visita /admin para administrar el sistema o /app para la aplicación'
    })