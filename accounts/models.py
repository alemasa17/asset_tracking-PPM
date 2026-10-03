from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "Utente"
        MANAGER = "manager", "Gestore inventario"
        ADMIN = "admin", "Amministratore"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)