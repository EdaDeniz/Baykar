from rest_framework import serializers
from .models import PartType, AircraftType, TeamType, Part, Aircraft

class PartTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartType
        fields = '__all__'

class AircraftTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftType
        fields = '__all__'

class TeamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamType
        fields = '__all__'

class PartSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='type.name', read_only=True)
    aircraft_type = serializers.CharField(source='aircraft_type.name', read_only=True)
    produced_by = serializers.CharField(source='produced_by.name', read_only=True)

    class Meta:
        model = Part
        fields = ['id', 'is_used', 'production_date', 'type', 'aircraft_type', 'produced_by']


class AircraftSerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True, read_only=True)

    class Meta:
        model = Aircraft
        fields = '__all__'