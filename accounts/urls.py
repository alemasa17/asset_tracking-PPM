# Pagine di login e logout già pronte in Django
from django.contrib.auth import views as auth_views
# path collega un indirizzo a una pagina
from django.urls import path

# Le view scritte sopra
from . import views

# Elenco degli indirizzi di questa app
urlpatterns = [
    # "/" apre la home; name serve per richiamarla nei template
    path("", views.home, name="home"),
    # "/login/" usa la pagina di login di Django con il nostro template
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    # "/logout/" chiude la sessione
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Aree protette
    path("gestione/", views.manager_area, name="manager_area"),
    path("amministrazione/", views.admin_area, name="admin_area"),
]