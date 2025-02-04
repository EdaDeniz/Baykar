from django.contrib import admin
from django.utils.html import format_html
from .models import PartType, AircraftType, TeamType, Staff, Part, Aircraft

@admin.register(PartType)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'managed_part_type', 'staff_count')
    list_filter = ('managed_part_type',)
    search_fields = ('name',)

    def staff_count(self, obj):
        return obj.staff.count()
    staff_count.short_description = 'Number of Staff'


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'team')
    list_filter = ('team',)
    search_fields = ('name',)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'aircraft_type', 'produced_by', 'is_used',
                    'production_date', 'status_color')
    list_filter = ('type', 'aircraft_type', 'produced_by', 'is_used')
    search_fields = ('type__name', 'aircraft_type__name')
    readonly_fields = ('production_date',)
    date_hierarchy = 'production_date'

    def status_color(self, obj):
        color = 'red' if obj.is_used else 'green'
        status = 'Used' if obj.is_used else 'Available'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            status
        )
    status_color.short_description = 'Status'


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'assembled_date', 'assembled_by', 'part_count')
    list_filter = ('type', 'assembled_by')
    search_fields = ('type__name',)
    readonly_fields = ('assembled_date',)
    date_hierarchy = 'assembled_date'
    filter_horizontal = ('parts',)

    def part_count(self, obj):
        return obj.parts.count()
    part_count.short_description = 'Number of Parts'

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # This will run the clean method before saving
        super().save_model(request, obj, form, change)