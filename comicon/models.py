from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


# -----------------------------
# Casa Editrice
# -----------------------------
class CasaEditrice(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        editore = Utente.objects.filter(ruolo='editore', casa_editrice=self).first()
        username = editore.username if editore else self.nome
        return f"{username} ({self.nome})"

# -----------------------------
# Fumetto
# -----------------------------
class Fumetto(models.Model):
    GENERI = [
        ("azione", "Azione"),
        ("avventura", "Avventura"),
        ("fantasy", "Fantasy"),
        ("horror", "Horror"),
        ("commedia", "Commedia"),
        ("drammatico", "Drammatico"),
        ("storico", "Storico"),
        ("altro", "Altro"),
    ]
    titolo = models.CharField(max_length=200)
    prezzo = models.DecimalField(max_digits=6, decimal_places=2)
    genere = models.CharField(max_length=100, choices=GENERI, default="altro")
    casa_editrice = models.ForeignKey(CasaEditrice, on_delete=models.CASCADE, related_name='fumetti')

    def __str__(self):
        casa = self.casa_editrice.nome if self.casa_editrice else "N/A"
        return f"{self.titolo} ({casa})"

# -----------------------------
# Generalizzazione Utenti
# -----------------------------
class Utente(AbstractUser):
    RUOLI = [
        ('utente', 'Utente'),
        ('autore', 'Autore'),
        ('editore', 'Casa Editrice'),
        ('admin', 'Amministratore'),
    ]
    ruolo = models.CharField(max_length=10, choices=RUOLI, default='utente')
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    casa_editrice = models.ForeignKey(CasaEditrice, null=True, blank=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'username'  # o 'email' se vuoi usarla come username
    REQUIRED_FIELDS = ['nome', 'cognome', 'email', 'ruolo']

    def __str__(self):
        return f"{self.nome} {self.cognome} ({self.get_ruolo_display()})"

# -----------------------------
# Autore (figura gestita tramite Utente con ruolo='autore')
# -----------------------------
class Autore(models.Model):
    utente = models.OneToOneField(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': 'autore'})
    opera_principale = models.OneToOneField(Fumetto, on_delete=models.CASCADE, related_name='autore_opera', null=True, blank=True)
    GIORNI = [
        ('2026-04-23', '2026-04-23'),
        ('2026-04-24', '2026-04-24'),
        ('2026-04-25', '2026-04-25'),
        ('2026-04-26', '2026-04-26'),
    ]
    giorni_disponibili = models.CharField(max_length=10, choices=GIORNI, default='2026-04-23')
    ORARI = [
        ("11:30-13:30", "11:30-13:30"),
        ("14:00-16:00", "14:00-16:00"),
        ("16:30-18:30", "16:30-18:30"),
    ]
    orari_disponibili = models.CharField(max_length=20, choices=ORARI, default="11:30-13:30")
    casa_editrice = models.ForeignKey(CasaEditrice, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        nome = self.utente.nome if self.utente and self.utente.nome else "(nome mancante)"
        cognome = self.utente.cognome if self.utente and self.utente.cognome else "(cognome mancante)"
        opera = self.opera_principale.titolo if self.opera_principale else "(nessuna opera)"
        casa = self.casa_editrice.nome if self.casa_editrice else "N/A"
        return f"{nome} {cognome} - {opera} ({casa})"

# -----------------------------
# Stand
# -----------------------------
class Stand(models.Model):
    PADIGLIONI = [(i, str(i)) for i in range(1, 7)]
    STALLI = [(i, str(i)) for i in range(1, 7)]
    disponibilita = models.BooleanField(default=True)
    padiglione = models.IntegerField(choices=PADIGLIONI)
    stallo = models.IntegerField(choices=STALLI, default=1)
    totale_persone = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"Padiglione {self.padiglione} - Stallo {self.stallo} - {self.totale_persone} persone"

# -----------------------------
# Prodotti (altri prodotti acquistabili)
# -----------------------------
class Prodotto(models.Model):
    nome = models.CharField(max_length=100)
    prezzo = models.DecimalField(max_digits=6, decimal_places=2)
    casa_editrice = models.ForeignKey(CasaEditrice, on_delete=models.CASCADE, related_name='prodotti')

    def __str__(self):
        return self.nome

# -----------------------------
# Disponibilità
# -----------------------------
class Disponibilita(models.Model):
    autore = models.ForeignKey(Autore, on_delete=models.CASCADE)
    data = models.DateField()
    orario = models.CharField(max_length=20, default="11:30-13:30")

    def __str__(self):
        data = self.data.strftime('%Y-%m-%d') if self.data else "Data non assegnata"
        orario = self.orario if self.orario else "Orario non assegnato"
        autore = str(self.autore) if self.autore else "Autore non assegnato"
        return f"{data} - {orario} ({autore})"

# -----------------------------
# Prenotazione Ticket: Unificazione di prenotazione e registrazione evento
# ---------------------
class Prenotazione(models.Model):
    utente = models.ForeignKey(Utente, on_delete=models.CASCADE, limit_choices_to={'ruolo': 'utente'}, related_name='prenotazioni')
    firmacopie = models.ForeignKey('FirmaCopie', on_delete=models.CASCADE, related_name='prenotazioni')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utente', 'firmacopie')  # Un utente può prenotare una sola volta per evento
        verbose_name_plural = 'Prenotazioni'

    def __str__(self):
        return f"Ticket per {self.utente} a {self.firmacopie}"

    def stampa_ticket(self):
        opera_titolo = self.firmacopie.autore.opera_principale.titolo if self.firmacopie.autore.opera_principale else "Opera non assegnata"
        stand_info = f"Padiglione {self.firmacopie.stand.padiglione}, Stallo {self.firmacopie.stand.stallo}" if self.firmacopie.stand else "Stand non assegnato"
        return f"""
        ---- TICKET COMICON 2026 ----
        Nome: {self.utente.nome} {self.utente.cognome}
        Email: {self.utente.email}
        Autore: {self.firmacopie.autore}
        Opera: {opera_titolo}
        Data: {self.firmacopie.data}
        Ora: {self.firmacopie.ora}
        Stand: {stand_info}
        Data Prenotazione: {self.timestamp}
        -----------------------------
        """



class ProdottoEditore(models.Model):
    """
    ⚠️ DEPRECATO: Usare Prodotto al suo posto.
    Questo modello esiste solo per compatibilità con le migrazioni precedenti.
    Sarà rimosso nella prossima migrazione.
    """
    casa_editrice = models.ForeignKey(CasaEditrice, on_delete=models.CASCADE)
    titolo = models.CharField(max_length=100)
    prezzo = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.titolo


class Genere(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

@receiver(post_save, sender=Utente)
def crea_ruolo_automatico(sender, instance, created, **kwargs):
    if created:
        from .models import Autore, CasaEditrice
        if instance.ruolo == 'autore' and not Autore.objects.filter(utente=instance).exists():
            Autore.objects.create(utente=instance, casa_editrice=instance.casa_editrice)
        if instance.ruolo == 'editore' and not CasaEditrice.objects.filter(nome=instance.nome).exists():
            CasaEditrice.objects.create(nome=instance.nome)
            # Associa la casa editrice appena creata all'utente
            instance.casa_editrice = CasaEditrice.objects.get(nome=instance.nome)
            instance.save()

# FirmaCopie: Evento di firma delle copie
class FirmaCopie(models.Model):
    autore = models.ForeignKey(Autore, on_delete=models.CASCADE, related_name='eventi_firmacopie')
    disponibilita = models.ForeignKey(Disponibilita, on_delete=models.CASCADE, related_name='eventi_firmacopie')
    stand = models.ForeignKey(Stand, on_delete=models.CASCADE, related_name='eventi_firmacopie')

    class Meta:
        unique_together = ('disponibilita', 'stand')  # Un evento per disponibilita/stand
        verbose_name_plural = 'FirmaCopie'

    def __str__(self):
        return f"{self.autore} - {self.data} {self.ora}"
    
    @property
    def casa_editrice(self):
        """Proprietà derivata dalla casa editrice dell'autore"""
        return self.autore.casa_editrice
    
    @property
    def data(self):
        """Data dell'evento (da Disponibilita)"""
        return self.disponibilita.data if self.disponibilita else None
    
    @property
    def ora(self):
        """Orario dell'evento (da Disponibilita)"""
        return self.disponibilita.orario if self.disponibilita else None
    
    def get_posti_disponibili(self):
        """Calcola i posti disponibili dinamicamente"""
        posti_totali = self.stand.totale_persone if self.stand else 0
        posti_occupati = Prenotazione.objects.filter(firmacopie=self).count()
        return posti_totali - posti_occupati

class Recensione(models.Model):
    utente = models.ForeignKey('Utente', on_delete=models.CASCADE)
    firmacopie = models.ForeignKey('FirmaCopie', on_delete=models.CASCADE)
    testo = models.TextField(max_length=1000)
    voto = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utente', 'firmacopie')

    def __str__(self):
        return f"Recensione di {self.utente} per {self.firmacopie}: {self.voto} stelle"

# Signal: Aggiorna la disponibilità dello stand quando viene creato un FirmaCopie
@receiver(post_save, sender=FirmaCopie)
def aggiorna_disponibilita_stand(sender, instance, created, **kwargs):
    """
    Quando un FirmaCopie viene creato o modificato, 
    aggiorna la disponibilità dello stand a False perché è occupato.
    """
    if instance.stand:
        # Se uno stand ha un FirmaCopie associato, non è più disponibile
        stand = instance.stand
        # Verifica se ci sono altri FirmaCopie associati a questo stand
        altri_eventi = FirmaCopie.objects.filter(stand=stand).exclude(id=instance.id).exists()
        stand.disponibilita = not altri_eventi  # Disponibile solo se non ci sono altri eventi
        stand.save()
