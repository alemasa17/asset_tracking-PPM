from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.permissions import role_required

from .forms import AssetCreateForm, AssetUpdateForm
from .models import Asset, Movement


@login_required
def asset_list(request):
    assets = Asset.objects.select_related("category", "location", "holder")
    return render(request, "assets/asset_list.html", {"assets": assets})


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(
        Asset.objects.select_related("category", "location", "holder"), pk=pk
    )
    movements = asset.movements.select_related("user", "from_location", "to_location")
    return render(
        request,
        "assets/asset_detail.html",
        {"asset": asset, "movements": movements},
    )


# Inserimento di un bene: solo gestore e amministratore
@role_required(User.Role.MANAGER)
def asset_create(request):
    if request.method == "POST":
        # Il modulo riceve i dati inviati dal browser
        form = AssetCreateForm(request.POST)
        # is_valid() esegue tutti i controlli (campi obbligatori, codice unico...)
        if form.is_valid():
            # atomic: o si salvano entrambe le righe, o nessuna
            with transaction.atomic():
                asset = form.save()
                Movement.objects.create(
                    asset=asset,
                    user=request.user,
                    action=Movement.Action.CREATED,
                    to_location=asset.location,
                )
            messages.success(request, f"Bene «{asset.name}» inserito.")
            # Dopo un salvataggio si reindirizza: ricaricare la pagina non reinvia il modulo
            return redirect("asset_detail", pk=asset.pk)
    else:
        # Prima visita (GET): modulo vuoto
        form = AssetCreateForm()
    return render(request, "assets/asset_form.html", {"form": form, "title": "Nuovo bene"})


# Modifica dei dati di un bene
@role_required(User.Role.MANAGER)
def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    # Un bene dismesso è chiuso: non si modifica
    if asset.status == Asset.Status.RETIRED:
        messages.warning(request, "Un bene dismesso non può essere modificato.")
        return redirect("asset_detail", pk=asset.pk)
    if request.method == "POST":
        # instance=asset dice che si modifica una riga esistente, non se ne crea una nuova
        form = AssetUpdateForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, "Modifiche salvate.")
            return redirect("asset_detail", pk=asset.pk)
    else:
        # GET: il modulo parte già compilato con i dati attuali
        form = AssetUpdateForm(instance=asset)
    return render(
        request,
        "assets/asset_form.html",
        {"form": form, "title": f"Modifica {asset.name}", "asset": asset},
    )


# Dismissione: il bene resta in archivio con tutto il suo storico
@role_required(User.Role.MANAGER)
@require_POST
def asset_retire(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if asset.status == Asset.Status.RETIRED:
        messages.warning(request, "Il bene è già dismesso.")
    else:
        with transaction.atomic():
            asset.status = Asset.Status.RETIRED
            asset.holder = None
            asset.save()
            Movement.objects.create(
                asset=asset,
                user=request.user,
                action=Movement.Action.RETIRED,
                from_location=asset.location,
            )
        messages.success(request, f"Bene «{asset.name}» dismesso.")
    return redirect("asset_detail", pk=asset.pk)