from rest_framework import serializers
from .models import Ksiazka, Kategoria, Wypozyczenie

class KategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategoria
        fields = '__all__'

class KsiazkaSerializer(serializers.ModelSerializer):
    kategoria = KategoriaSerializer(read_only=True)
    
    class Meta:
        model = Ksiazka
        fields = '__all__'

class WypozyczenieSerializer(serializers.ModelSerializer):
    ksiazka = KsiazkaSerializer(read_only=True)
    
    class Meta:
        model = Wypozyczenie
        fields = '__all__'