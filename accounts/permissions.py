# wraps conserva nome e descrizione della pagina originale
from functools import wraps

# Strumento di Django: manda al login chi non ha fatto accesso
from django.contrib.auth.decorators import login_required
# Errore "403 Vietato", da sollevare quando il ruolo non basta
from django.core.exceptions import PermissionDenied


# Costruisce un "controllo" da attaccare sopra una pagina, indicando il ruolo minimo
def role_required(minimum_role):
    # Riceve la pagina (view) da proteggere
    def decorator(view_func):
        # Prima controlla il login, poi il ruolo
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Se il ruolo è troppo basso, risponde 403
            if not request.user.has_role_at_least(minimum_role):
                raise PermissionDenied
            # Altrimenti esegue la pagina vera
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator