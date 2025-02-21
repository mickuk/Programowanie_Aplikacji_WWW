from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Ksiazka, Wypozyczenie
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .serializers import KsiazkaSerializer
import xml.etree.ElementTree as ET
from django.template.loader import render_to_string
from datetime import date, timedelta
from .forms import KsiazkaForm
from .filters import WypozyczenieFilter



class KsiazkaViewSet(viewsets.ModelViewSet):
    queryset = Ksiazka.objects.all()
    serializer_class = KsiazkaSerializer


@api_view(['GET'])
def export_ksiazki_xml(request):
    ksiazki = Ksiazka.objects.all()
    root = ET.Element('ksiazki')
    
    for ksiazka in ksiazki:
        book_elem = ET.SubElement(root, 'ksiazka')
        ET.SubElement(book_elem, 'tytul').text = ksiazka.tytul
        ET.SubElement(book_elem, 'autor').text = ksiazka.autor
        ET.SubElement(book_elem, 'rok').text = str(ksiazka.rok_wydania)
        
    tree = ET.ElementTree(root)
    response = HttpResponse(content_type='application/xml')
    tree.write(response, encoding='unicode', xml_declaration=True)
    return response


def lista_ksiazek(request):
    ksiazki_lista = Ksiazka.objects.all().order_by('tytul')
    paginator = Paginator(ksiazki_lista, 12)  # 12 książek na stronę
    
    page = request.GET.get('page')
    ksiazki = paginator.get_page(page)
    
    return render(request, 'ksiazki/lista_ksiazek.html', {'ksiazki': ksiazki})


def szczegoly_ksiazki(request, pk):
    ksiazka = get_object_or_404(Ksiazka, pk=pk)
    return render(request, 'ksiazki/szczegoly_ksiazki.html', {'ksiazka': ksiazka})


@login_required
def wypozycz_ksiazke(request, pk):
    if request.user.is_staff:
        messages.error(request, 'Pracownicy biblioteki nie mogą wypożyczać książek.')
        return redirect('szczegoly_ksiazki', pk=pk)
    
    ksiazka = get_object_or_404(Ksiazka, pk=pk)
    
    # Sprawdź czy użytkownik nie ma już oczekującej lub aktywnej prośby o tę książkę
    if Wypozyczenie.objects.filter(ksiazka=ksiazka, czytelnik=request.user, data_zwrotu=None).exists():
        messages.error(request, 'Już złożyłeś prośbę o tę książkę lub ją wypożyczyłeś.')
        return redirect('szczegoly_ksiazki', pk=pk)
        
    if not ksiazka.dostepna:
        messages.error(request, 'Ta książka jest obecnie niedostępna.')
        return redirect('szczegoly_ksiazki', pk=pk)
        
    Wypozyczenie.objects.create(
        ksiazka=ksiazka,
        czytelnik=request.user
    )
    
    messages.success(request, 'Prośba o wypożyczenie została złożona.')
    return redirect('moje_wypozyczenia')

@login_required
def moje_wypozyczenia(request):
    # Pokaż tylko własne niezatwierdzone i zatwierdzone wypożyczenia
    wypozyczenia = Wypozyczenie.objects.filter(
        czytelnik=request.user, 
        data_zwrotu=None
    ).order_by('-data_wypozyczenia')
    
    for wypozyczenie in wypozyczenia:
        wypozyczenie.nalicz_oplate()  # Automatyczne naliczanie opłat
    
    return render(request, 'ksiazki/moje_wypozyczenia.html', {'wypozyczenia': wypozyczenia})


@user_passes_test(lambda u: u.is_staff)
def lista_wypozyczen(request):
    wypozyczenia = Wypozyczenie.objects.filter(zatwierdzone=False).order_by('-data_wypozyczenia')
    return render(request, 'ksiazki/lista_wypozyczen.html', {'wypozyczenia': wypozyczenia})


@login_required
@user_passes_test(lambda u: u.is_staff)  # Upewniamy się, że tylko administrator może zatwierdzać
def zatwierdz_wypozyczenie(request, pk):
    wypozyczenie = get_object_or_404(Wypozyczenie, pk=pk)
    if not wypozyczenie.zatwierdzone:
        wypozyczenie.zatwierdzone = True
        wypozyczenie.ksiazka.dostepna = False
        wypozyczenie.ksiazka.save()
        wypozyczenie.save()
        messages.success(request, f'Wypożyczenie książki "{wypozyczenie.ksiazka.tytul}" zostało zatwierdzone.')
    else:
        messages.info(request, 'To wypożyczenie zostało już zatwierdzone.')
    return redirect('lista_wypozyczen')


@login_required
def przedluz_wypozyczenie(request, pk):
    wypozyczenie = get_object_or_404(Wypozyczenie, pk=pk, czytelnik=request.user)
    if wypozyczenie.przedluz():
        messages.success(request, "Wypożyczenie zostało przedłużone o 30 dni.")
    else:
        messages.error(request, "Nie można przedłużyć tego wypożyczenia.")
    return redirect('moje_wypozyczenia')

@login_required
@user_passes_test(lambda u: u.is_staff)
def zatwierdz_zwrot(request, pk):
    wypozyczenie = get_object_or_404(Wypozyczenie, pk=pk)
    if wypozyczenie.czy_mozna_zwrocic():
        wypozyczenie.data_zwrotu = date.today()
        wypozyczenie.ksiazka.dostepna = True
        wypozyczenie.ksiazka.save()
        wypozyczenie.save()
        messages.success(request, 'Książka została zwrócona.')
    else:
        messages.error(request, 'Nie można zwrócić tej książki.')
    return redirect('lista_wypozyczen')


@login_required
@user_passes_test(lambda u: u.is_staff)  # Upewniamy się, że tylko administrator może opłacić zaległość
def approve_overdue_payment(request, pk):
    wypozyczenie = get_object_or_404(Wypozyczenie, pk=pk)
    if wypozyczenie.oplata > 0:
        wypozyczenie.oplata = 0
        wypozyczenie.save()
        messages.success(request, f'Opłata za spóźnienie dla książki "{wypozyczenie.ksiazka.tytul}" została opłacona.')
    else:
        messages.info(request, 'Brak zaległości do opłacenia.')
    return redirect('lista_wypozyczen')


@login_required
def dodaj_ksiazke(request):
    if request.user.is_staff:  # Tylko administrator może dodawać książki
        if request.method == 'POST':
            form = KsiazkaForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Książka została pomyślnie dodana.')
                return redirect('lista_ksiazek')
        else:
            form = KsiazkaForm()
        return render(request, 'ksiazki/dodaj_ksiazke.html', {'form': form})
    else:
        messages.error(request, 'Nie masz uprawnień do dodawania książek.')
        return redirect('lista_ksiazek')
    


@login_required
@user_passes_test(lambda u: u.is_staff)
def odrzuc_wypozyczenie(request, pk):
    wypozyczenie = get_object_or_404(Wypozyczenie, pk=pk)
    if not wypozyczenie.zatwierdzone:
        ksiazka = wypozyczenie.ksiazka
        ksiazka.dostepna = True
        ksiazka.save()
        wypozyczenie.delete()
        messages.success(request, f'Prośba o wypożyczenie książki "{ksiazka.tytul}" została odrzucona.')
    return redirect('lista_wypozyczen')



@user_passes_test(lambda u: u.is_staff)
def lista_wypozyczen(request):
    pending = Wypozyczenie.objects.filter(zatwierdzone=False).order_by('-data_wypozyczenia')
    active = Wypozyczenie.objects.filter(zatwierdzone=True, data_zwrotu=None).order_by('-data_wypozyczenia')
    return render(request, 'ksiazki/lista_wypozyczen.html', {
        'pending': pending,
        'active': active
    })


def rents_list(request):
    rents = Wypozyczenie.objects.all().order_by('-overdue', '-rent_date')  # Sortowanie: najpierw zaległość, potem data wypożyczenia malejąco
    return render(request, 'ksiazki/rents_list.html', {'rents': rents})



@login_required
def edytuj_ksiazke(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Nie masz uprawnień do edycji książek.')
        return redirect('szczegoly_ksiazki', pk=pk)
    
    ksiazka = get_object_or_404(Ksiazka, pk=pk)
    
    if request.method == 'POST':
        form = KsiazkaForm(request.POST, request.FILES, instance=ksiazka)
        if form.is_valid():
            form.save()
            messages.success(request, 'Książka została zaktualizowana.')
            return redirect('szczegoly_ksiazki', pk=pk)
    else:
        form = KsiazkaForm(instance=ksiazka)
    
    return render(request, 'ksiazki/edytuj_ksiazke.html', {'form': form, 'ksiazka': ksiazka})