# autenticacion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Vista HTML para login
    path('', views.login_view, name='login'),
    
    # Vista HTML para logout
    path('logout/', views.logout_view, name='logout'),
]