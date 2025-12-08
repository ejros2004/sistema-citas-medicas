# autenticacion/urls_api.py
from django.urls import path
from .views import (
    LoginAPIView,
    LogoutAPIView,
    RegistroAPIView,
    UserDetailAPIView,
    CambioPasswordAPIView,
    UserListAPIView,
    UserAdminAPIView,
    verificar_autenticacion,
    debug_info
)

urlpatterns = [
    # Autenticación
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('registro/', RegistroAPIView.as_view(), name='api_registro'),
    path('verificar/', verificar_autenticacion, name='api_verificar'),
    
    # Usuario actual
    path('user/', UserDetailAPIView.as_view(), name='api_user_detail'),
    path('cambiar-password/', CambioPasswordAPIView.as_view(), name='api_cambiar_password'),
    
    # Admin (solo administradores)
    path('users/', UserListAPIView.as_view(), name='api_user_list'),
    path('users/<int:user_id>/', UserAdminAPIView.as_view(), name='api_user_admin'),
    
    # Debug
    path('debug/', debug_info, name='api_debug'),
]