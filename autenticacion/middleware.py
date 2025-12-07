# autenticacion/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
import re

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = '/login/'
        self.exempt_urls = [
            re.compile(r'^/login/$'),
            re.compile(r'^/logout/$'),
            re.compile(r'^/admin/'),
            re.compile(r'^/static/'),
            re.compile(r'^/media/'),
            re.compile(r'^/api/autenticacion/login/$'),
            re.compile(r'^/api/autenticacion/registro/$'),
        ]
    
    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            
            # Verificar si la URL está exenta
            if not any(url.match(path) for url in self.exempt_urls):
                return redirect(f'{self.login_url}?next={path}')
        
        response = self.get_response(request)
        return response

class RolMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Aquí puedes agregar lógica adicional basada en roles
        # por ejemplo, verificar acceso a ciertas URLs
        return None