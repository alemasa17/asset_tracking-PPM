# Controllo "serve il login"
from django.contrib.auth.decorators import login_required
# Prepara una pagina HTML a partire da un template
from django.shortcuts import render

# Il tuo modello utente e il controllo per ruolo
from .models import User
from .permissions import role_required


# Home: basta aver fatto login
@login_required
def home(request):
    # Mostra il template home.html
    return render(request, "accounts/home.html")


# Area gestione: serve almeno il ruolo gestore
@role_required(User.Role.MANAGER)
def manager_area(request):
    return render(request, "accounts/manager_area.html")


# Area amministrazione: serve il ruolo amministratore
@role_required(User.Role.ADMIN)
def admin_area(request):
    return render(request, "accounts/admin_area.html")