from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.permissions import role_required

from .forms import AssetCreateForm, AssetMoveForm, AssetUpdateForm
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
        form = AssetCreateForm(request.POST)
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
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = AssetCreateForm()
    return render(request, "assets/asset_form.html", {"form": form, "title": "Nuovo bene"})


# Modifica dei dati di un bene
@role_required(User.Role.MANAGER)
def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if asset.status == Asset.Status.RETIRED:
        messages.warning(request, "Un bene dismesso non può essere modificato.")
        return redirect("asset_detail", pk=asset.pk)
    if request.method == "POST":
        form = AssetUpdateForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, "Modifiche salvate.")
            return redirect("asset_detail", pk=asset.pk)
    else:
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


# Presa in carico: qualsiasi utente connesso può prendere un bene disponibile
@login_required
@require_POST
def asset_checkout(request, pk):
    with transaction.atomic():
        asset = get_object_or_404(Asset.objects.select_for_update(), pk=pk)
        if asset.status != Asset.Status.AVAILABLE:
            messages.warning(request, "Il bene non è disponibile.")
            return redirect("asset_detail", pk=asset.pk)
        asset.status = Asset.Status.IN_USE
        asset.holder = request.user
        asset.save()
        Movement.objects.create(
            asset=asset,
            user=request.user,
            action=Movement.Action.CHECKED_OUT,
        )
    messages.success(request, f"Hai preso in carico «{asset.name}».")
    return redirect("asset_detail", pk=asset.pk)


# Restituzione: il responsabile, oppure gestore e amministratore
@login_required
@require_POST
def asset_return(request, pk):
    with transaction.atomic():
        asset = get_object_or_404(Asset.objects.select_for_update(), pk=pk)
        if asset.status != Asset.Status.IN_USE:
            messages.warning(request, "Il bene non è in uso.")
            return redirect("asset_detail", pk=asset.pk)
        if asset.holder_id != request.user.id and not request.user.can_manage_inventory:
            raise PermissionDenied
        asset.status = Asset.Status.AVAILABLE
        asset.holder = None
        asset.save()
        Movement.objects.create(
            asset=asset,
            user=request.user,
            action=Movement.Action.RETURNED,
        )
    messages.success(request, f"«{asset.name}» restituito.")
    return redirect("asset_detail", pk=asset.pk)


# Chi può spostare un bene: mai se dismesso; se disponibile chiunque;
# se in uso solo il responsabile oppure chi gestisce l'inventario
def can_move(user, asset):
    if asset.status == Asset.Status.RETIRED:
        return False
    return (
        asset.status == Asset.Status.AVAILABLE
        or asset.holder_id == user.id
        or user.can_manage_inventory
    )


@login_required
def asset_move(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if not can_move(request.user, asset):
        raise PermissionDenied
    if request.method == "POST":
        form = AssetMoveForm(request.POST, asset=asset)
        if form.is_valid():
            with transaction.atomic():
                # Si rilegge il bene con il blocco: nel frattempo può essere cambiato
                asset = get_object_or_404(Asset.objects.select_for_update(), pk=pk)
                if not can_move(request.user, asset):
                    raise PermissionDenied
                old_location = asset.location
                asset.location = form.cleaned_data["location"]
                asset.save()
                Movement.objects.create(
                    asset=asset,
                    user=request.user,
                    action=Movement.Action.MOVED,
                    from_location=old_location,
                    to_location=asset.location,
                    note=form.cleaned_data["note"],
                )
            messages.success(request, f"«{asset.name}» spostato in {asset.location}.")
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = AssetMoveForm(asset=asset)
    return render(
        request,
        "assets/asset_form.html",
        {"form": form, "title": f"Sposta {asset.name}", "asset": asset},
    )