from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Ruolo", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_staff")
        # Mostra il ruolo anche nel modulo di creazione di un nuovo utente
    add_fieldsets = UserAdmin.add_fieldsets + (("Ruolo", {"fields": ("role",)}),)
    