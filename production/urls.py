from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartViewSet, AircraftViewSet

router = DefaultRouter()
router.register(r'parts', PartViewSet, 'part')
router.register(r'aircraft', AircraftViewSet, 'aircraft')

urlpatterns = [
    path('api/', include(router.urls)),

]
