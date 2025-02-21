from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return self.nazwa

class Ksiazka(models.Model):
    tytul = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    opis = models.TextField()
    rok_wydania = models.IntegerField()
    kategoria = models.ForeignKey(Kategoria, on_delete=models.SET_NULL, null=True)
    dostepna = models.BooleanField(default=True)  # Dostępność książki
    okladka = models.ImageField(upload_to='okladki/', null=True, blank=True)
    data_dodania = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Książki"

    def __str__(self):
        return f"{self.tytul} - {self.autor}"

class Wypozyczenie(models.Model):
    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.CASCADE)
    czytelnik = models.ForeignKey(User, on_delete=models.CASCADE)
    data_wypozyczenia = models.DateTimeField(auto_now_add=True)
    data_zwrotu = models.DateTimeField(null=True, blank=True)  # Data faktycznego zwrotu
    zatwierdzone = models.BooleanField(default=False)
    uwagi = models.TextField(blank=True)
    przedluzenie = models.BooleanField(default=False)  # Czy wypożyczenie było przedłużone
    oplata = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Naliczone opłaty

    class Meta:
        verbose_name_plural = "Wypożyczenia"

    def przewidywana_data_zwrotu(self):
        """
        Oblicza przewidywaną datę zwrotu książki:
        - 30 dni dla standardowego wypożyczenia,
        - 60 dni, jeśli wypożyczenie zostało przedłużone.
        """
        if self.przedluzenie:
            return self.data_wypozyczenia + timedelta(days=60)
        return self.data_wypozyczenia + timedelta(days=30)

    def przedluz(self):
        """
        Przedłuż wypożyczenie o dodatkowe 30 dni, jeśli jeszcze tego nie zrobiono.
        """
        if not self.zatwierdzone or self.przedluzenie:
            return False  # Nie można przedłużyć niezatwierdzonego lub już przedłużonego wypożyczenia
        self.przedluzenie = True
        self.save()
        return True

    def nalicz_oplate(self):
        """
        Nalicz opłatę za spóźnienie:
        - 0.10 PLN za każdy rozpoczęty dzień po terminie zwrotu.
        """
        if self.zatwierdzone:
            dzis = date.today()
            opoznienie = max((dzis - self.przewidywana_data_zwrotu().date()).days, 0)
            self.oplata = round(opoznienie * 0.10, 2)
            self.save()

    def czy_mozna_zwrocic(self):
        return self.zatwierdzone and not self.data_zwrotu and self.oplata == 0

    def __str__(self):
        return f"{self.ksiazka.tytul} - {self.czytelnik.username}"



@receiver(post_save, sender=Wypozyczenie)
def aktualizuj_dostepnosc_ksiazki_po_zapisie(sender, instance, created, **kwargs):
    if created or instance.zatwierdzone:
        instance.ksiazka.dostepna = bool(instance.data_zwrotu)
        instance.ksiazka.save()