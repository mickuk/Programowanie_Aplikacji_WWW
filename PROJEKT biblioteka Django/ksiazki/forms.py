from django import forms
from .models import Ksiazka

class KsiazkaForm(forms.ModelForm):
    class Meta:
        model = Ksiazka
        fields = ['tytul', 'autor', 'isbn', 'opis', 'rok_wydania', 'kategoria', 'okladka', 'dostepna']