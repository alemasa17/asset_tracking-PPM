# Strumenti di Django per costruire i moduli
from django import forms

from .models import Asset, Location


# Aggiunge le classi di Bootstrap a tutti i campi, per averli larghi e curati
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # I menu a tendina usano una classe diversa dai campi di testo
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = css


# Modulo di inserimento: include il luogo iniziale
class AssetCreateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        # Django costruisce i campi a partire dal modello Asset
        model = Asset
        fields = ["name", "inventory_code", "description", "category", "location", "purchase_date"]
        widgets = {
            # type=date mostra il selettore di data del browser
            "purchase_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            # Casella di testo alta tre righe
            "description": forms.Textarea(attrs={"rows": 3}),
        }


# Modulo di modifica: senza luogo, che cambia solo con gli spostamenti
class AssetUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Asset
        fields = ["name", "inventory_code", "description", "category", "purchase_date"]
        widgets = AssetCreateForm.Meta.widgets


class AssetMoveForm(BootstrapFormMixin, forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label="Nuovo luogo")
    note = forms.CharField(label="Nota", max_length=255, required=False)

    def __init__(self, *args, asset, **kwargs):
        super().__init__(*args, **kwargs)
        # Il menu non propone il luogo in cui il bene si trova già
        self.fields["location"].queryset = Location.objects.exclude(pk=asset.location_id)