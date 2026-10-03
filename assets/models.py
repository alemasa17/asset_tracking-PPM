# Importa le impostazioni del progetto: serve per sapere qual è il modello utente
from django.conf import settings
# Importa gli strumenti di Django per definire tabelle e colonne
from django.db import models


# Tabella delle categorie (es. Computer, Arredi)
class Category(models.Model):
    # Colonna "nome": testo breve, massimo 100 caratteri, senza doppioni
    name = models.CharField("nome", max_length=100, unique=True)

    # Impostazioni generali della tabella
    class Meta:
        # Nome italiano al singolare, mostrato nel pannello admin
        verbose_name = "categoria"
        # Nome italiano al plurale
        verbose_name_plural = "categorie"
        # Ordine predefinito: alfabetico per nome
        ordering = ["name"]

    # Stabilisce come si presenta una categoria quando viene mostrata come testo
    def __str__(self):
        # Mostra semplicemente il suo nome
        return self.name


# Tabella dei luoghi (es. "Reggio - Magazzino")
class Location(models.Model):
    # Colonna "nome": testo breve, unico
    name = models.CharField("nome", max_length=100, unique=True)
    # Colonna "descrizione": testo lungo, può restare vuota
    description = models.TextField("descrizione", blank=True)

    # Impostazioni generali della tabella
    class Meta:
        # Nome italiano al singolare
        verbose_name = "luogo"
        # Nome italiano al plurale
        verbose_name_plural = "luoghi"
        # Ordine alfabetico per nome
        ordering = ["name"]

    # Come si presenta un luogo come testo
    def __str__(self):
        # Mostra il suo nome
        return self.name


# Tabella dei beni: il cuore del sistema
class Asset(models.Model):
    # Elenco chiuso degli stati possibili di un bene
    class Status(models.TextChoices):
        # Nome nel codice = valore salvato nel database, etichetta mostrata all'utente
        AVAILABLE = "available", "Disponibile"
        # Il bene è in carico a qualcuno
        IN_USE = "in_use", "In uso"
        # Il bene è stato rottamato, ma resta in archivio
        RETIRED = "retired", "Dismesso"

    # Nome del bene (es. "Misuratore laser")
    name = models.CharField("nome", max_length=200)
    # Codice inventario: unico, due beni non possono avere lo stesso
    inventory_code = models.CharField("codice inventario", max_length=50, unique=True)
    # Descrizione libera, facoltativa
    description = models.TextField("descrizione", blank=True)
    # Collegamento alla categoria del bene
    category = models.ForeignKey(
        # Tabella collegata; PROTECT vieta di cancellare una categoria che contiene beni;
        # related_name permette di scrivere categoria.assets; poi l'etichetta italiana
        Category, on_delete=models.PROTECT, related_name="assets", verbose_name="categoria"
    )
    # Collegamento al luogo in cui si trova il bene
    location = models.ForeignKey(
        # Stessa logica: non si può cancellare un luogo che contiene beni
        Location, on_delete=models.PROTECT, related_name="assets", verbose_name="luogo"
    )
    # Stato attuale del bene
    status = models.CharField(
        # Etichetta, lunghezza massima, valori ammessi, valore iniziale "Disponibile"
        "stato", max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    # Responsabile: l'utente che ha il bene in carico
    holder = models.ForeignKey(
        # Collega alla tabella User definita in accounts
        settings.AUTH_USER_MODEL,
        # Se l'utente viene eliminato, il bene resta e il campo si svuota
        on_delete=models.SET_NULL,
        # Nel database il campo può non avere valore (bene senza responsabile)
        null=True,
        # Nei moduli il campo può essere lasciato vuoto
        blank=True,
        # Permette di scrivere utente.held_assets per avere i beni che ha in carico
        related_name="held_assets",
        # Etichetta italiana
        verbose_name="responsabile",
    )
    # Data di acquisto, facoltativa
    purchase_date = models.DateField("data di acquisto", null=True, blank=True)
    # Data e ora di inserimento, scritte automaticamente da Django alla creazione
    created_at = models.DateTimeField("inserito il", auto_now_add=True)

    # Impostazioni generali della tabella
    class Meta:
        # Nome italiano al singolare
        verbose_name = "bene"
        # Nome italiano al plurale
        verbose_name_plural = "beni"
        # Ordine alfabetico per nome
        ordering = ["name"]

    # Come si presenta un bene come testo
    def __str__(self):
        # Esempio: "Misuratore laser (INV-001)"
        return f"{self.name} ({self.inventory_code})"


# Tabella dei movimenti: lo storico, una riga per ogni evento
class Movement(models.Model):
    # Elenco chiuso dei tipi di evento
    class Action(models.TextChoices):
        # Il bene è stato inserito nel sistema
        CREATED = "created", "Inserito"
        # Un utente lo ha preso in carico
        CHECKED_OUT = "checked_out", "Preso in carico"
        # Un utente lo ha restituito
        RETURNED = "returned", "Restituito"
        # È stato spostato da un luogo a un altro
        MOVED = "moved", "Spostato"
        # È stato rottamato
        RETIRED = "retired", "Dismesso"

    # Il bene a cui si riferisce l'evento
    asset = models.ForeignKey(
        # CASCADE: se il bene viene eliminato del tutto, il suo storico va con lui;
        # related_name permette di scrivere bene.movements per avere il suo storico
        Asset, on_delete=models.CASCADE, related_name="movements", verbose_name="bene"
    )
    # L'utente che ha compiuto l'azione
    user = models.ForeignKey(
        # Collega alla tabella User
        settings.AUTH_USER_MODEL,
        # PROTECT: non si può eliminare un utente che compare nello storico
        on_delete=models.PROTECT,
        # Permette di scrivere utente.movements per avere le sue azioni
        related_name="movements",
        # Etichetta italiana
        verbose_name="utente",
    )
    # Il tipo di evento, scelto dall'elenco Action
    action = models.CharField("azione", max_length=20, choices=Action.choices)
    # Luogo di partenza (compilato solo per gli spostamenti)
    from_location = models.ForeignKey(
        # Se il luogo viene eliminato il campo si svuota; può restare vuoto
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        # "+" significa: il percorso inverso (luogo -> movimenti) non serve
        related_name="+", verbose_name="da",
    )
    # Luogo di arrivo (compilato solo per gli spostamenti)
    to_location = models.ForeignKey(
        # Stessa logica del luogo di partenza
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        # Anche qui il percorso inverso non serve
        related_name="+", verbose_name="a",
    )
    # Nota facoltativa (es. "portato in riparazione")
    note = models.CharField("nota", max_length=255, blank=True)
    # Data e ora dell'evento, scritte automaticamente: nessuno può falsificarle
    timestamp = models.DateTimeField("data e ora", auto_now_add=True)

    # Impostazioni generali della tabella
    class Meta:
        # Nome italiano al singolare
        verbose_name = "movimento"
        # Nome italiano al plurale
        verbose_name_plural = "movimenti"
        # Ordine dal più recente al più vecchio (il meno inverte l'ordine)
        ordering = ["-timestamp"]

    # Come si presenta un movimento come testo
    def __str__(self):
        # Esempio: "Preso in carico - Misuratore laser (INV-001) - giulia"
        return f"{self.get_action_display()} - {self.asset} - {self.user}"