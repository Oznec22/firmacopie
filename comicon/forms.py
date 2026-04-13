from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CasaEditrice, Autore, Fumetto, Genere, Prodotto, Disponibilita, Recensione  # tutti i modelli che ti servono


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class AutoreForm(forms.ModelForm):
    casa_editrice = forms.ModelChoiceField(
        queryset=CasaEditrice.objects.all(),
        required=False,
        empty_label="Nessuna"
    )

    class Meta:
        model = Autore
        fields = ['giorni_disponibili', 'orari_disponibili', 'casa_editrice']


class AssociaAutoriForm(forms.Form):
    autore = forms.ModelChoiceField(
        queryset=Autore.objects.none(),
        label="Autore da associare",
        required=True
    )

    def __init__(self, *args, **kwargs):
        casa_editrice = kwargs.pop('casa_editrice', None)
        super().__init__(*args, **kwargs)
        if casa_editrice:
            # Filtra autori che hanno un'opera principale della casa editrice
            self.fields['autore'].queryset = Autore.objects.filter(
                casa_editrice=casa_editrice
            ).distinct()
        else:
            self.fields['autore'].queryset = Autore.objects.all()


class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = ['nome', 'prezzo']
        labels = {
            'nome': 'Titolo prodotto',
            'prezzo': 'Prezzo (€)'
        }


class DisponibilitaForm(forms.ModelForm):
    data = forms.ChoiceField(choices=[('', '---')] + Autore.GIORNI, label='Giorno')
    orario = forms.ChoiceField(choices=[('', '---')] + Autore.ORARI, label='Orario')

    class Meta:
        model = Disponibilita
        fields = ['data', 'orario']
        labels = {
            'data': 'Giorno',
            'orario': 'Orario'
        }


class RecensioneForm(forms.ModelForm):
    class Meta:
        model = Recensione
        fields = ['testo', 'voto']
        labels = {
            'testo': 'La tua recensione',
            'voto': 'Voto (1-5 stelle)'
        }
