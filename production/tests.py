from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import PartType, AircraftType, TeamType, Part, Aircraft, UserProfile

class PartViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.team = TeamType.objects.create(name='Engine Team')
        self.part_type = PartType.objects.create(name='Engine', description='Aircraft engine')
        self.aircraft_type = AircraftType.objects.create(name='Fighter Jet', description='Military aircraft')
        self.team.managed_part_type = self.part_type
        self.team.save()
        UserProfile.objects.create(user=self.user, team=self.team)
        self.client.login(username='testuser', password='testpass')

    def test_get_parts(self):
        response = self.client.get('/api/parts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_part(self):
        data = {
            'type': self.part_type.id,
            'aircraft_type': self.aircraft_type.id,
            'produced_by': self.team.id
        }
        response = self.client.post('/api/parts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class AircraftViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', password='testpass')
        self.team = TeamType.objects.create(name='Montaj Takımı')
        self.part_type = PartType.objects.create(name='Wing', description='Aircraft wing')
        self.aircraft_type = AircraftType.objects.create(name='Cargo Plane', description='Transport aircraft')
        self.part = Part.objects.create(type=self.part_type, aircraft_type=self.aircraft_type, produced_by=self.team)
        UserProfile.objects.create(user=self.user, team=self.team)
        self.client.login(username='testuser2', password='testpass')

    def test_get_aircraft(self):
        response = self.client.get('/api/aircraft/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_aircraft_with_parts(self):
        data = {'type': self.aircraft_type.id, 'parts': [self.part.id]}
        response = self.client.post('/api/aircraft/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
