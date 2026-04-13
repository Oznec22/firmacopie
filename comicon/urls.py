from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from .views import elimina_disponibilita

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('registrazione/', views.registrazione_view, name='registrazione'),
    path('home/', views.home_redirect_view, name='home_redirect'),
    path('logout/', LogoutView.as_view(next_page='landing_page'), name='logout'),
    path('home/utente/', views.home_utente_view, name='home_utente'),
    path('home/autore/', views.home_autore_view, name='home_autore'),
    path('home/editore/', views.home_editore_view, name='home_editore'),
    path('home/autore/crea/', views.crea_aggiorna_profilo_autore, name='crea_profilo_autore'),
    path('home/editore/autore/<int:autore_id>/elimina/', views.elimina_autore_editore, name='elimina_autore_editore'),
    path('home/autore/disponibilita/<int:disp_id>/elimina/', elimina_disponibilita, name='elimina_disponibilita'),
    path('home/editore/prodotto/<int:prodotto_id>/modifica/', views.modifica_prodotto, name='modifica_prodotto'),
    path('home/editore/prodotto/<int:prodotto_id>/elimina/', views.elimina_prodotto, name='elimina_prodotto'),
    path('admin/comicon/ajax/casa_editrice_autore/', views.ajax_casa_editrice_autore, name='ajax_casa_editrice_autore'),
]
