from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartViewSet, AircraftViewSet, available_parts, assemble_aircraft

router = DefaultRouter()
router.register(r'parts', PartViewSet, 'part')
router.register(r'aircraft', AircraftViewSet, 'aircraft')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/aircraft/assemble/', assemble_aircraft, name='assemble_aircraft'),
    path('api/parts/available/<int:aircraft_type_id>/', available_parts, name='available_parts'),
]
