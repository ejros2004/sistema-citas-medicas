from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet

router = DefaultRouter()
router.register(r'', CitaViewSet, basename='cita')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints específicos para estados
    path('<int:pk>/confirmar/', CitaViewSet.as_view({'put': 'confirmar'}), name='cita-confirmar'),
    path('<int:pk>/cancelar/', CitaViewSet.as_view({'put': 'cancelar'}), name='cita-cancelar'),
    path('<int:pk>/finalizar/', CitaViewSet.as_view({'put': 'finalizar'}), name='cita-finalizar'),
]