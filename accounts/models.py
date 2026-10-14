# Strumenti di Django: l'utente standard e quelli per definire le tabelle
from django.contrib.auth.models import AbstractUser
from django.db import models

# Livello di ogni ruolo: più alto = più poteri. I ruoli sono cumulativi
ROLE_LEVELS = {"user": 1, "manager": 2, "admin": 3}


# Il tuo utente: eredita tutto dall'utente standard di Django
class User(AbstractUser):
    # Elenco chiuso dei ruoli ammessi
    class Role(models.TextChoices):
        USER = "user", "Utente"
        MANAGER = "manager", "Gestore inventario"
        ADMIN = "admin", "Amministratore"

    # Colonna del ruolo: parte sempre da "Utente"
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    # Risponde alla domanda: "questo utente ha almeno questo ruolo?"
    def has_role_at_least(self, minimum_role):
        # Confronta il livello del suo ruolo con quello richiesto
        return ROLE_LEVELS.get(self.role, 0) >= ROLE_LEVELS[str(minimum_role)]

    # Scorciatoia per i template: può gestire l'inventario? (gestore o amministratore)
    @property
    def can_manage_inventory(self):
        return self.has_role_at_least("manager")

    # Scorciatoia per i template: è amministratore?
    @property
    def can_administer(self):
        return self.has_role_at_least("admin")