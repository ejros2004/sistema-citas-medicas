# autenticacion/urls_api.py - COMPLETO
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
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('registro/', RegistroAPIView.as_view(), name='api_registro'),
    path('verificar/', verificar_autenticacion, name='api_verificar'),  # ¡IMPORTANTE!
    path('user/', UserDetailAPIView.as_view(), name='api_user_detail'),
    path('cambiar-password/', CambioPasswordAPIView.as_view(), name='api_cambiar_password'),
    path('users/', UserListAPIView.as_view(), name='api_user_list'),
    path('users/<int:user_id>/', UserAdminAPIView.as_view(), name='api_user_admin'),
    path('debug/', debug_info, name='api_debug'),
]