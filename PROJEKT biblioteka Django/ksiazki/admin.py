from datetime import date
from django.contrib import admin
from .models import Ksiazka, Kategoria, Wypozyczenie

@admin.register(Kategoria)
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis')
    search_fields = ('nazwa',)

@admin.register(Ksiazka)
class KsiazkaAdmin(admin.ModelAdmin):
    list_display = ('tytul', 'autor', 'isbn', 'kategoria', 'dostepna', 'rok_wydania', 'data_dodania')
    list_filter = ('kategoria', 'dostepna', 'rok_wydania')
    search_fields = ('tytul', 'autor', 'isbn')
    ordering = ('tytul',)

@admin.register(Wypozyczenie)
class WypozyczenieAdmin(admin.ModelAdmin):
    list_display = ('ksiazka', 'czytelnik', 'data_wypozyczenia', 'przewidywana_data_zwrotu', 'zatwierdzone', 'przedluzenie', 'oplata')
    list_filter = ('zatwierdzone', 'przedluzenie')
    search_fields = ('ksiazka__tytul', 'czytelnik__username')
    actions = ['zatwierdz_wypozyczenie', 'zatwierdz_zwrot']

    @admin.action(description='Zatwierdź wypożyczenie')
    def zatwierdz_wypozyczenie(self, request, queryset):
        for wypozyczenie in queryset:
            if not wypozyczenie.zatwierdzone:
                wypozyczenie.zatwierdzone = True
                wypozyczenie.ksiazka.dostepna = False
                wypozyczenie.ksiazka.save()
                wypozyczenie.save()

    @admin.action(description='Zatwierdź zwrot')
    def zatwierdz_zwrot(self, request, queryset):
        for wypozyczenie in queryset:
            if wypozyczenie.zatwierdzone and not wypozyczenie.data_zwrotu:
                wypozyczenie.data_zwrotu = date.today()
                wypozyczenie.ksiazka.dostepna = True
                wypozyczenie.ksiazka.save()
                wypozyczenie.nalicz_oplate()
                wypozyczenie.save()
