# autenticacion/middleware.py - COMPLETO
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path
        
        print(f"🛡️  Middleware: {path} | Autenticado: {request.user.is_authenticated} | Usuario: {request.user}")
        
        if path == '/login/' and request.user.is_authenticated:
            print(f"📍 Middleware: Usuario ya autenticado en /login/, redirigiendo a /app/")
            return redirect('/app/')
        
        if path == '/' and request.user.is_authenticated:
            print(f"📍 Middleware: Usuario ya autenticado en raíz, redirigiendo a /app/")
            return redirect('/app/')
        
        if not request.user.is_authenticated and path == '/app/':
            print(f"🔒 Middleware: Usuario no autenticado intentando acceder a /app/, redirigiendo a /login/")
            return redirect('/login/')
        
        return self.get_response(request)


class RolMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)