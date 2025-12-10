from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicoViewSet, EspecialidadViewSet

router = DefaultRouter()
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'medicos', MedicoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]