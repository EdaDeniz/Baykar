from django.db import models
from django.core.exceptions import ValidationError


class PartType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()


class AircraftType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()


class TeamType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    managed_part_type = models.ForeignKey(PartType, null=True, blank=True, on_delete=models.SET_NULL)


class Staff(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(TeamType, related_name='staff', on_delete=models.CASCADE)


class Part(models.Model):
    type = models.ForeignKey(PartType, on_delete=models.CASCADE)
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE)
    produced_by = models.ForeignKey(TeamType, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    production_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.produced_by.managed_part_type != self.type:
            raise ValidationError('Team can only produce their assigned part type')


class Aircraft(models.Model):
    type = models.ForeignKey(AircraftType, on_delete=models.CASCADE)
    assembled_date = models.DateTimeField(auto_now_add=True)
    assembled_by = models.ForeignKey(TeamType, on_delete=models.CASCADE)
    parts = models.ManyToManyField(Part)

    def clean(self):
        for part in self.parts.all():
            if part.aircraft_type != self.type:
                raise ValidationError(f'Incompatible part type')
            if part.is_used:
                raise ValidationError('Cannot use already used parts')
