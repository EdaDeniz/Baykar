from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from production.models import PartType, AircraftType


@login_required
def homepage(request):
    context = {
        'part_types': PartType.objects.all(),
        'aircraft_types': AircraftType.objects.all()
    }
    return render(request, 'dashboard.html', context)