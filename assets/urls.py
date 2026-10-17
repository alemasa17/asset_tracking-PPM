# path collega un indirizzo a una pagina
from django.urls import path

# Le view scritte sopra
from . import views

# Indirizzi di questa app
urlpatterns = [
    # "/beni/" mostra l'elenco
    path("beni/", views.asset_list, name="asset_list"),
    # "/beni/3/" mostra la scheda del bene numero 3; <int:pk> cattura il numero
    path("beni/<int:pk>/", views.asset_detail, name="asset_detail"),
]