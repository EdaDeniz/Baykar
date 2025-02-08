# forms.py
from django import forms
from .models import Aircraft, Part, AircraftType

class AircraftAssemblyForm(forms.Form):
    aircraft_type = forms.ModelChoiceField(
        queryset=AircraftType.objects.all(),
        label="Aircraft Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)

        # Dynamically create fields for each part type
        self.available_parts = Part.objects.filter(is_used=False)

        # Group available parts by type
        part_types = self.available_parts.values_list('type__name', flat=True).distinct()

        for part_type in part_types:
            field_name = f'part_{part_type.lower().replace(" ", "_")}'
            parts_of_type = self.available_parts.filter(type__name=part_type)

            self.fields[field_name] = forms.ModelChoiceField(
                queryset=parts_of_type,
                label=f"Select {part_type}",
                required=True,
                widget=forms.Select(attrs={'class': 'form-select'})
            )

    def clean(self):
        cleaned_data = super().clean()
        aircraft_type = cleaned_data.get('aircraft_type')

        if not aircraft_type:
            raise forms.ValidationError("Aircraft type is required")

        # Collect all selected parts
        selected_parts = []
        for field_name, value in cleaned_data.items():
            if field_name.startswith('part_') and value:
                selected_parts.append(value)

        # Validate team permission
        if self.team.name != "Assembly Set":
            raise forms.ValidationError("Only Assembly team can assemble aircraft")

        # Validate part compatibility
        for part in selected_parts:
            if part.aircraft_type != aircraft_type:
                raise forms.ValidationError(
                    f"Incompatible part: {part.type.name} is not compatible with {aircraft_type.name}"
                )
            if part.is_used:
                raise forms.ValidationError(
                    f"Part {part.type.name} (ID: {part.id}) is already used"
                )

        # Store selected parts for use in view
        self.cleaned_data['selected_parts'] = selected_parts

        return cleaned_data