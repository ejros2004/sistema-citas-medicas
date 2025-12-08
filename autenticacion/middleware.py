# autenticacion/middleware.py
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    """
    Middleware SIMPLIFICADO para evitar bucles de redirección.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path
        
        # Debug
        print(f"🛡️  Middleware: {path} | Autenticado: {request.user.is_authenticated} | Usuario: {request.user}")
        
        # REGLA 1: Si está en /login/ y YA está autenticado → /app/
        if path == '/login/' and request.user.is_authenticated:
            print(f"📍 Middleware: Usuario ya autenticado en /login/, redirigiendo a /app/")
            return redirect('/app/')
        
        # REGLA 2: Si está en raíz '/' y YA está autenticado → /app/
        if path == '/' and request.user.is_authenticated:
            print(f"📍 Middleware: Usuario ya autenticado en raíz, redirigiendo a /app/")
            return redirect('/app/')
        
        # REGLA 3: Si NO está autenticado y quiere acceder a /app/ → /login/
        if not request.user.is_authenticated and path == '/app/':
            print(f"🔒 Middleware: Usuario no autenticado intentando acceder a /app/, redirigiendo a /login/")
            return redirect('/login/')
        
        # REGLA 4: Todo OK, continuar
        return self.get_response(request)


class RolMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Esta middleware no hace nada por ahora, solo pasa la request
        return self.get_response(request)