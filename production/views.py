from django.db.models import Count
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Part, Aircraft, PartType, AircraftType, UserProfile
from .serializers import PartSerializer, AircraftSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class PartViewSet(viewsets.ModelViewSet):
    """API viewset for Part model"""
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter parts based on user's team"""
        user_profile = UserProfile.objects.get(user=self.request.user)
        user_team = user_profile.team
        parts = Part.objects.filter(produced_by=user_team)
        return parts

    def perform_create(self, serializer):
        """Set the producing team when creating a part"""
        user_profile = UserProfile.objects.get(user=self.request.user)
        user_team = user_profile.team

        # Validate part type against team's managed part type
        try:
            part_type = PartType.objects.get(id=self.request.data['type'])
        except PartType.DoesNotExist:
            raise ValidationError({"type": "Invalid part type selected."})

        if part_type != user_team.managed_part_type:
            raise ValidationError({"type": f"Your team can only create {user_team.managed_part_type.name} parts."})

        serializer.save(produced_by=user_team)

    def destroy(self, request, *args, **kwargs):
        """Override delete to implement 'recycle' functionality"""
        part = self.get_object()
        if part.is_used:
            return Response(
                {"error": "Cannot recycle a part that is already used in an aircraft"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def available_parts(self, request):
        """Get available parts for a specific aircraft type"""
        aircraft_type_id = request.query_params.get('aircraft_type')
        if not aircraft_type_id:
            return Response(
                {"error": "aircraft_type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        parts = Part.objects.filter(
            aircraft_type_id=aircraft_type_id,
            is_used=False
        ).select_related('type')

        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inventory_status(self, request):
        """Get inventory status for all aircraft types"""
        aircraft_types = AircraftType.objects.all()
        status_data = {}

        for aircraft in aircraft_types:
            parts = Part.objects.filter(
                aircraft_type=aircraft,
                is_used=False
            ).values('type__name').annotate(count=Count('id'))

            missing_parts = []
            for part_type in PartType.objects.all():
                if not any(p['type__name'] == part_type.name for p in parts):
                    missing_parts.append(part_type.name)

            status_data[aircraft.name] = {
                'available_parts': {p['type__name']: p['count'] for p in parts},
                'missing_parts': missing_parts
            }

        return Response(status_data)

class AircraftViewSet(viewsets.ModelViewSet):
    """API viewset for Aircraft model"""
    serializer_class = AircraftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Aircraft.objects.all()

    def perform_create(self, serializer):
        """Create aircraft with parts validation"""
        user_profile = UserProfile.objects.get(user=self.request.user)
        user_team = user_profile.team

        if user_team.name != "Assembly Set":
            raise ValidationError("Only Assembly team can create aircraft")

        if user_team.name != "Assembly Set":
            raise ValidationError("Only Assembly team can create aircraft")

        part_ids = self.request.data.getlist('parts', [])
        parts = Part.objects.filter(id__in=part_ids)

        if not part_ids or parts.count() != len(part_ids):
            raise ValidationError("Some parts are missing or invalid.")

        aircraft_type_id = self.request.data.get("type")
        if not aircraft_type_id:
            raise ValidationError("Aircraft type is required.")

        try:
            aircraft_type = AircraftType.objects.get(id=aircraft_type_id)
        except AircraftType.DoesNotExist:
            raise ValidationError("Invalid aircraft type selected.")

        # Check required parts
        required_part_types = set(PartType.objects.values_list('name', flat=True))
        provided_part_types = set(part.type.name for part in parts)

        if required_part_types != provided_part_types:
            missing_parts = required_part_types - provided_part_types
            raise ValidationError(f"Missing required parts: {', '.join(missing_parts)}")

        for part in parts:
            if part.is_used:
                raise ValidationError(f"Part {part} is already used")
            if part.aircraft_type_id != aircraft_type.id:
                raise ValidationError(f"Part {part} is not compatible with this aircraft type")

        with transaction.atomic():
            aircraft = serializer.save(type=aircraft_type, assembled_by=user_team)
            aircraft.parts.set(parts)
            parts.update(is_used=True)

    @action(detail=False, methods=['get'])
    def assembly_status(self, request):
        """Get assembly status and available parts for each aircraft type"""
        aircraft_types = AircraftType.objects.all()
        status_data = {}

        for aircraft_type in aircraft_types:
            available_parts = Part.objects.filter(
                aircraft_type=aircraft_type,
                is_used=False
            ).select_related('type')

            parts_by_type = {}
            for part in available_parts:
                if part.type.name not in parts_by_type:
                    parts_by_type[part.type.name] = []
                parts_by_type[part.type.name].append({
                    'id': part.id,
                    'production_date': part.production_date
                })

            status_data[aircraft_type.name] = {
                'id': aircraft_type.id,
                'available_parts': parts_by_type,
                'can_assemble': all(
                    len(parts) > 0
                    for parts in parts_by_type.values()
                )
            }

        return Response(status_data)