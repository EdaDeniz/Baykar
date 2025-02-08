from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json

from .models import Part, Aircraft, TeamType, PartType, AircraftType, UserProfile
from .forms import AircraftAssemblyForm
from .serializers import PartSerializer, AircraftSerializer, TeamTypeSerializer

@login_required
def home(request):
    """Home page view showing dashboard"""
    user_profile = UserProfile.objects.get(user=request.user)
    user_team = user_profile.team
    context = {
        'aircraft_types': AircraftType.objects.all(),
        'user_team': user_team
    }
    return render(request, 'home.html', context)

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
        """Ensure only Assembly team can create aircraft"""
        user_profile = UserProfile.objects.get(user=self.request.user)
        user_team = user_profile.team
        if user_team.name != "Assembly Set":
            raise ValidationError("Only Assembly team can create aircraft")
        serializer.save(assembled_by=user_team)

@require_http_methods(["POST"])
@login_required
def assemble_aircraft(request):
    """Handle aircraft assembly AJAX requests"""
    try:
        data = json.loads(request.body)
        user_profile = UserProfile.objects.get(user=request.user)
        user_team = user_profile.team
        # Validate team
        if user_team.name != "Assembly Set":
            return JsonResponse({
                "message": "Only Assembly team can assemble aircraft"
            }, status=403)

        # Validate aircraft type
        try:
            aircraft_type = AircraftType.objects.get(id=data['aircraft_type'])
        except AircraftType.DoesNotExist:
            return JsonResponse({
                "message": "Invalid aircraft type",
                "field_errors": {
                    "aircraft_type": "Please select a valid aircraft type"
                }
            }, status=400)

        # Collect and validate parts
        selected_parts = []
        field_errors = {}

        for field_name, part_id in data['parts'].items():
            try:
                part = Part.objects.get(id=part_id, is_used=False)
                if part.aircraft_type != aircraft_type:
                    field_errors[field_name] = f"This part is not compatible with {aircraft_type.name}"
                else:
                    selected_parts.append(part)
            except Part.DoesNotExist:
                field_errors[field_name] = "Selected part is no longer available"

        if field_errors:
            return JsonResponse({
                "message": "Invalid parts selected",
                "field_errors": field_errors
            }, status=400)

        # Validate complete set of parts
        required_part_types = set(PartType.objects.values_list('name', flat=True))
        provided_part_types = set(part.type.name for part in selected_parts)

        if required_part_types != provided_part_types:
            missing_parts = required_part_types - provided_part_types
            return JsonResponse({
                "message": f"Missing required parts: {', '.join(missing_parts)}"
            }, status=400)

        # Create aircraft with atomic transaction
        with transaction.atomic():

            user_profile = UserProfile.objects.get(user=request.user)
            user_team = user_profile.team
            aircraft = Aircraft.objects.create(
                type=aircraft_type,
                assembled_by=user_team
            )

            # Mark parts as used and associate with aircraft
            for part in selected_parts:
                part.is_used = True
                part.save()

            aircraft.parts.set(selected_parts)

        return JsonResponse({
            "message": f"Successfully assembled {aircraft_type.name}",
            "aircraft_id": aircraft.id
        })

    except Exception as e:
        return JsonResponse({
            "message": str(e)
        }, status=500)

@require_http_methods(["GET"])
@login_required
def available_parts(request, aircraft_type_id):
    """Get available parts for an aircraft type"""
    try:
        aircraft_type = AircraftType.objects.get(id=aircraft_type_id)
        parts = Part.objects.filter(
            aircraft_type=aircraft_type,
            is_used=False
        ).select_related('type')

        # Group parts by type
        parts_by_type = {}
        for part in parts:
            if part.type.name not in parts_by_type:
                parts_by_type[part.type.name] = []
            parts_by_type[part.type.name].append({
                'id': part.id,
                'production_date': part.production_date
            })

        return JsonResponse(parts_by_type)

    except AircraftType.DoesNotExist:
        return JsonResponse({
            "message": "Invalid aircraft type"
        }, status=404)

@require_http_methods(["POST"])
@login_required
def create_part(request):
    """Handle part creation AJAX requests"""
    try:
        data = json.loads(request.body)
        user_profile = UserProfile.objects.get(user=request.user)
        user_team = user_profile.team

        # Validate part type against team's managed part type
        try:
            part_type = PartType.objects.get(id=data['type'])
            if part_type != user_team.managed_part_type:
                return JsonResponse({
                    "message": f"Your team can only create {user_team.managed_part_type.name} parts"
                }, status=403)
        except PartType.DoesNotExist:
            return JsonResponse({
                "message": "Invalid part type"
            }, status=400)

        # Create the part
        part = Part.objects.create(
            type=part_type,
            aircraft_type_id=data['aircraft_type'],
            produced_by=user_team
        )

        return JsonResponse({
            "message": "Part created successfully",
            "part_id": part.id
        })

    except Exception as e:
        return JsonResponse({
            "message": str(e)
        }, status=500)

@login_required
def part_list(request):
    """View for listing parts"""
    user_profile = UserProfile.objects.get(user=request.user)
    user_team = user_profile.team
    parts = Part.objects.filter(produced_by=user_team)
    return render(request, 'part_list.html', {'parts': parts})

@login_required
def aircraft_list(request):
    """View for listing aircraft"""
    aircraft = Aircraft.objects.all()
    return render(request, 'aircraft_list.html', {'aircraft': aircraft})