from django import forms
from comicon.models import Autore

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
            self.fields['autore'].queryset = Autore.objects.filter(casa_editrice=casa_editrice)
        else:
            self.fields['autore'].queryset = Autore.objects.all()
