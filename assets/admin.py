from django.contrib import admin

from .models import Asset, Category, Location, Movement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "inventory_code", "category", "location", "status", "holder")
    list_filter = ("status", "category", "location")
    search_fields = ("name", "inventory_code")


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "asset", "action", "user", "from_location", "to_location")
    list_filter = ("action",)