from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'medicos', views.MedicoViewSet, basename='medico')
router.register(r'especialidades', views.EspecialidadViewSet, basename='especialidad')

urlpatterns = [
    path('', include(router.urls)),
]