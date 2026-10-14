# Pannello admin e include (importa gli indirizzi di un'altra app)
from django.contrib import admin
from django.urls import include, path

# Indirizzi principali del progetto
urlpatterns = [
    # "/admin/" resta il pannello di Django
    path("admin/", admin.site.urls),
    # Tutto il resto lo gestisce l'app accounts
    path("", include("accounts.urls")),
]