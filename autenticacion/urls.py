# autenticacion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ================= VISTAS HTML =================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('dashboard/', views.dashboard_view, name='dashboard'), 

    # ================= VISTAS API =================
    # Rutas explícitas que coinciden con tu Middleware y JS
    path('api/autenticacion/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/autenticacion/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/autenticacion/registro/', views.RegistroAPIView.as_view(), name='api_registro'),
    path('api/autenticacion/verificar/', views.verificar_autenticacion, name='api_verificar'),
    
    # Otras rutas de usuario
    path('api/autenticacion/usuario/', views.UserDetailAPIView.as_view(), name='api_usuario_detalle'),
    path('api/autenticacion/cambio-password/', views.CambioPasswordAPIView.as_view(), name='api_cambio_password'),
]