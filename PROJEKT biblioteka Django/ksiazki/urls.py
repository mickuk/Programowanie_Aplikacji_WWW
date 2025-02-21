from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
from .views import KsiazkaViewSet

router = DefaultRouter()
router.register(r'api/ksiazki', KsiazkaViewSet)

urlpatterns = [
    path('', views.lista_ksiazek, name='lista_ksiazek'),
    path('ksiazka/<int:pk>/', views.szczegoly_ksiazki, name='szczegoly_ksiazki'),
    path('wypozycz/<int:pk>/', views.wypozycz_ksiazke, name='wypozycz_ksiazke'),
    path('moje-wypozyczenia/', views.moje_wypozyczenia, name='moje_wypozyczenia'),
    path('lista-wypozyczen/', views.lista_wypozyczen, name='lista_wypozyczen'),
    path('zatwierdz-wypozyczenie/<int:pk>/', views.zatwierdz_wypozyczenie, name='zatwierdz_wypozyczenie'),
    path('', include(router.urls)),
    path('export/xml/', views.export_ksiazki_xml, name='export_xml'),
    path('przedluz-wypozyczenie/<int:pk>/', views.przedluz_wypozyczenie, name='przedluz_wypozyczenie'),
    path('dodaj-ksiazke/', views.dodaj_ksiazke, name='dodaj_ksiazke'),
    path('odrzuc-wypozyczenie/<int:pk>/', views.odrzuc_wypozyczenie, name='odrzuc_wypozyczenie'),
    path('zatwierdz-zwrot/<int:pk>/', views.zatwierdz_zwrot, name='zatwierdz_zwrot'),
    path('edytuj-ksiazke/<int:pk>/', views.edytuj_ksiazke, name='edytuj_ksiazke'),

]
