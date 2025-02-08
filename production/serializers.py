from rest_framework import serializers
from .models import PartType, AircraftType, TeamType, Part, Aircraft, UserProfile


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
    type_name = serializers.CharField(source='type.name', read_only=True)
    aircraft_type_name = serializers.CharField(source='aircraft_type.name', read_only=True)
    produced_by_name = serializers.CharField(source='produced_by.name', read_only=True)

    class Meta:
        model = Part
        exclude = ['produced_by']  # Exclude 'produced_by' from API input

    def create(self, validated_data):
        """Automatically set produced_by to the user's team"""
        request = self.context['request']
        user_team = UserProfile.objects.get(user=request.user).team
        validated_data['produced_by'] = user_team
        return super().create(validated_data)


class AircraftSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)
    parts = PartSerializer(many=True, read_only=True)
    assembled_by_name = serializers.CharField(source='assembled_by.name', read_only=True)

    class Meta:
        model = Aircraft
        fields = '__all__'
        read_only_fields = ['assembled_by']