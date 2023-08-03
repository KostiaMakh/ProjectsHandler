from django.contrib import admin

from projects.models import (
    Manufacture,
    Equipment,
    Location,
    Position,
    TechnologicalNode,
    Complectation
)


@admin.register(Complectation)
class ComplectationAdmin(admin.ModelAdmin):
    list_display = ('pk', )


@admin.register(TechnologicalNode)
class TechnologicalNodeAdmin(admin.ModelAdmin):
    pass


@admin.register(Manufacture)
class ManufactureAdmin(admin.ModelAdmin):
    pass


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass
