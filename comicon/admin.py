from django.contrib import admin
from .models import Utente, Autore, CasaEditrice, Fumetto, Prodotto, Stand, Disponibilita, Genere, FirmaCopie, Prenotazione
from django import forms

# Per consentire la gestione degli utenti personalizzati
@admin.register(Utente)
class UtenteAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'cognome', 'email', 'ruolo', 'casa_editrice')
    list_filter = ('ruolo', 'casa_editrice')
    search_fields = ('username', 'nome', 'cognome', 'email')

# Per gestire gli autori con il link all'utente e all'opera principale
@admin.register(Autore)
class AutoreAdmin(admin.ModelAdmin):
    list_display = ('utente', 'opera_principale', 'get_casa_editrice_username', 'giorni_disponibili', 'orari_disponibili')
    search_fields = ('utente__nome', 'utente__cognome', 'opera_principale__titolo')
    fields = ('utente', 'opera_principale', 'casa_editrice', 'giorni_disponibili', 'orari_disponibili')
    
    def get_casa_editrice_username(self, obj):
        if not obj.casa_editrice:
            return 'N/A'
        editore = Utente.objects.filter(ruolo='editore', casa_editrice=obj.casa_editrice).first()
        return editore.username if editore else obj.casa_editrice.nome
    get_casa_editrice_username.short_description = 'Casa Editrice (Username)'

@admin.register(CasaEditrice)
class CasaEditriceAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_editore_username')
    search_fields = ('nome',)
    readonly_fields = ('autori_affiliati',)

    def get_editore_username(self, obj):
        editore = Utente.objects.filter(ruolo='editore', casa_editrice=obj).first()
        return editore.username if editore else 'N/A'
    get_editore_username.short_description = 'Username Editore'

    def autori_affiliati(self, obj):
        autori = obj.autore_set.all()
        if autori:
            return ', '.join([str(a) for a in autori])
        return 'Nessun autore affiliato'
    autori_affiliati.short_description = 'Autori affiliati'

@admin.register(Fumetto)
class FumettoAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'prezzo', 'genere', 'casa_editrice')
    list_filter = ('casa_editrice', 'genere')
    search_fields = ('titolo',)

@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'prezzo', 'get_casa_editrice_username')
    list_filter = ('casa_editrice',)
    search_fields = ('nome',)

    def get_casa_editrice_username(self, obj):
        editore = Utente.objects.filter(ruolo='editore', casa_editrice=obj.casa_editrice).first()
        return editore.username if editore else 'N/A'
    get_casa_editrice_username.short_description = 'Casa Editrice (Username)'

# Gestione Stand con associazione a un solo autore e alla sua casa editrice
@admin.register(Stand)
class StandAdmin(admin.ModelAdmin):
    list_display = ('id', 'padiglione', 'stallo', 'totale_persone', 'disponibilita')
    list_filter = ('padiglione', 'stallo', 'disponibilita')
    search_fields = ('padiglione', 'stallo')

class DisponibilitaAdmin(admin.ModelAdmin):
    list_display = ('autore', 'data', 'orario')
    list_filter = ('data', 'orario', 'autore')
    search_fields = ('autore__utente__nome', 'autore__utente__cognome')
    readonly_fields = ('data', 'orario')

admin.site.register(Disponibilita, DisponibilitaAdmin)

class FirmaCopieForm(forms.ModelForm):
    class Meta:
        model = FirmaCopie
        exclude = ['data', 'ora', 'casa_editrice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stand'].queryset = Stand.objects.filter(disponibilita=True)

class FirmaCopieAdmin(admin.ModelAdmin):
    form = FirmaCopieForm
    list_display = ('autore', 'disponibilita', 'stand')
    list_filter = ('stand',)
    search_fields = ('autore__utente__nome', 'autore__utente__cognome')

admin.site.register(FirmaCopie, FirmaCopieAdmin)

class PrenotazioneAdmin(admin.ModelAdmin):
    list_display = ('utente', 'firmacopie', 'get_disponibilita', 'timestamp')
    search_fields = ('utente__nome', 'utente__cognome', 'firmacopie__autore__utente__nome')
    readonly_fields = ('timestamp',)

    def get_disponibilita(self, obj):
        if obj.firmacopie and obj.firmacopie.disponibilita:
            return str(obj.firmacopie.disponibilita)
        return "Disponibilità non assegnata"
    get_disponibilita.short_description = 'Disponibilità (data e orario)'

admin.site.register(Prenotazione, PrenotazioneAdmin)
admin.site.register(Genere)
