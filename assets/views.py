# Controllo "serve il login"
from django.contrib.auth.decorators import login_required
# get_object_or_404 cerca un oggetto e, se non esiste, mostra la pagina "non trovato"
from django.shortcuts import get_object_or_404, render

# La tabella dei beni
from .models import Asset


# Elenco di tutti i beni: lo vedono tutti i ruoli, basta il login
@login_required
def asset_list(request):
    # Chiede al database tutti i beni; select_related prende insieme anche
    # categoria, luogo e responsabile, invece di fare una richiesta per ogni riga
    assets = Asset.objects.select_related("category", "location", "holder")
    # Passa i beni al template con il nome "assets"
    return render(request, "assets/asset_list.html", {"assets": assets})


# Scheda di un singolo bene; pk è il numero identificativo del bene, preso dall'indirizzo
@login_required
def asset_detail(request, pk):
    # Cerca il bene con quel numero; se non esiste risponde 404
    asset = get_object_or_404(
        Asset.objects.select_related("category", "location", "holder"), pk=pk
    )
    # Il suo storico: "movements" è il nome (related_name) dato nel modello Movement
    movements = asset.movements.select_related("user", "from_location", "to_location")
    # Passa al template sia il bene sia lo storico
    return render(
        request,
        "assets/asset_detail.html",
        {"asset": asset, "movements": movements},
    )