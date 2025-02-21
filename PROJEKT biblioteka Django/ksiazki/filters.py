import django_filters
from .models import Wypozyczenie

class WypozyczenieFilter(django_filters.FilterSet):
    class Meta:
        model = Wypozyczenie
        fields = {
            'ksiazka__tytul': ['icontains'],
            'czytelnik__username': ['icontains'],
            'zatwierdzone': ['exact'],
        }
