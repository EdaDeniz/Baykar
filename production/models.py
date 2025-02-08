from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.core.exceptions import ValidationError


class PartType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class AircraftType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class TeamType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    managed_part_type = models.ForeignKey(PartType, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name



class Part(models.Model):
    type = models.ForeignKey(PartType, on_delete=models.CASCADE)
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE)
    produced_by = models.ForeignKey(TeamType, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    production_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.produced_by.managed_part_type != self.type:
            raise ValidationError('Team can only produce their assigned part type')

    def __str__(self):
        return f' {self.type.name} - {self.aircraft_type.name}'

class Aircraft(models.Model):
    type = models.ForeignKey(AircraftType, on_delete=models.CASCADE)
    assembled_date = models.DateTimeField(auto_now_add=True)
    assembled_by = models.ForeignKey(TeamType, on_delete=models.CASCADE)
    parts = models.ManyToManyField(Part)

    def clean_parts(self):
        for part in self.parts.all():
            if part.aircraft_type != self.type:
                raise ValidationError(f'Incompatible part type')
            if part.is_used:
                raise ValidationError('Cannot use already used parts')

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new object
        super().save(*args, **kwargs)  # Save first to get an ID
        if not is_new:  # Only validate parts if the object already exists
            self.clean_parts()

    def __str__(self):
        return f' {self.type.name} Aircraft'



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(TeamType, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.username} - {self.team.name if self.team else 'No Team'}"