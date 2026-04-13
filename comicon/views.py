from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django import forms  # ✅ NECESSARIO PER forms.ChoiceField, forms.CharField
from .models import Utente, Fumetto, Disponibilita, Autore, Prodotto, FirmaCopie, Stand, CasaEditrice, Prenotazione
from django.views.decorators.http import require_POST, require_GET  # 👈 risolve il NameError
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.db import transaction  # ✅ Per proteggere da race condition
from django.db.models import Count, Q  # ✅ Per ottimizzare query
from .forms import AutoreForm, AssociaAutoriForm, ProdottoForm, DisponibilitaForm
from django.forms import modelformset_factory

class FumettoForm(forms.ModelForm):
    casa_editrice = forms.ModelChoiceField(queryset=CasaEditrice.objects.all(), required=True, label='Casa Editrice')
    class Meta:
        model = Fumetto
        fields = ['titolo', 'genere', 'prezzo', 'casa_editrice']
        labels = {
            'titolo': 'Titolo',
            'genere': 'Genere',
            'prezzo': 'Prezzo (€)',
            'casa_editrice': 'Casa Editrice'
        }

def home(request):
    return HttpResponse("<h1>Benvenuto al portale Comicon 2026!</h1><p>Vai su <a href='/admin/'>/admin</a> per gestire l'evento.</p>")


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home_redirect')
    else:
        form = LoginForm()
    return render(request, 'comicon/login.html', {'form': form})


def home_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    ruolo = getattr(request.user, 'ruolo', None)
    if ruolo == 'autore':
        return redirect('home_autore')
    elif ruolo == 'editore':
        return redirect('home_editore')
    elif ruolo == 'utente':
        return redirect('home_utente')
    else:
        return render(request, 'comicon/errore_ruolo.html', {'messaggio': 'Il tuo profilo non ha un ruolo valido. Contatta l\'amministratore.'})




def landing_page(request):
    return render(request, 'comicon/landing_page.html')


# ✅ FORM DI REGISTRAZIONE CORRETTO
class RegistrazioneForm(UserCreationForm):
    RUOLI = [
        ('utente', 'Utente'),
        ('autore', 'Autore'),
        ('editore', 'Casa Editrice'),
    ]

    ruolo = forms.ChoiceField(choices=RUOLI)
    nome = forms.CharField(max_length=100)
    cognome = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = Utente
        fields = ['username', 'nome', 'cognome', 'email', 'ruolo', 'password1', 'password2']

@login_required
def home_utente_view(request):
    if request.user.ruolo != 'utente':
        return render(request, 'comicon/errore_ruolo.html', {'messaggio': 'Accesso non consentito: ruolo non valido per questa pagina.'})

    # ✅ OTTIMIZZAZIONE: Fetch con select_related per evitare N+1 queries
    eventi = FirmaCopie.objects.select_related(
        'autore', 'autore__utente', 'autore__opera_principale', 
        'disponibilita', 'stand'
    ).all()
    
    # ✅ OTTIMIZZAZIONE: Annotate per conteggio prenotazioni in una sola query
    eventi = eventi.annotate(
        posti_occupati=Count('prenotazioni')
    )
    
    # Prenotazioni dell'utente
    prenotazioni_utente = Prenotazione.objects.filter(utente=request.user).select_related('firmacopie')
    eventi_prenotati = [p.firmacopie for p in prenotazioni_utente if p.firmacopie is not None]
    eventi_ids_prenotati = [e.id for e in eventi_prenotati if hasattr(e, 'id')]

    # Gestione prenotazione/cancellazione
    if request.method == 'POST':
        evento_id = request.POST.get('evento_id')
        
        if 'prenota' in request.POST:
            # ✅ PROTEZIONE: Transazione atomica per evitare race condition
            with transaction.atomic():
                evento = FirmaCopie.objects.select_for_update().get(id=evento_id)
                posti_disponibili = evento.get_posti_disponibili()
                
                # Verifica che non sia già prenotato (unique_together previene duplicati a livello DB)
                if posti_disponibili > 0 and not Prenotazione.objects.filter(
                    utente=request.user, firmacopie=evento
                ).exists():
                    Prenotazione.objects.create(utente=request.user, firmacopie=evento)
                    messages.success(request, 'Prenotazione effettuata!')
                else:
                    messages.error(request, 'Posti esauriti o già prenotato!')
                    
        elif 'annulla' in request.POST:
            evento = FirmaCopie.objects.get(id=evento_id)
            Prenotazione.objects.filter(utente=request.user, firmacopie=evento).delete()
            messages.success(request, 'Prenotazione annullata!')
            
        return redirect('home_utente')

    # Per ogni evento prepara le info con posti disponibili
    eventi_info = []
    for evento in eventi:
        posti_totali = evento.stand.totale_persone if evento.stand else 0
        posti_disponibili = posti_totali - evento.posti_occupati  # Usa il valore annotated
        
        eventi_info.append({
            'evento': evento,
            'posti_occupati': evento.posti_occupati,
            'posti_totali': posti_totali,
            'posti_disponibili': posti_disponibili,
            'prenotato': evento.id in eventi_ids_prenotati,
            'casa_editrice': evento.autore.casa_editrice.nome if evento.autore.casa_editrice else 'N/A',
        })

    # Recupera tutte le case editrici e i loro prodotti
    case_editrici = CasaEditrice.objects.all()
    case_prodotti = []
    for casa in case_editrici:
        prodotti = casa.prodotti.all()
        editore = Utente.objects.filter(ruolo='editore', casa_editrice=casa).first()
        username = editore.username if editore else 'N/A'
        case_prodotti.append({
            'casa': casa,
            'prodotti': prodotti,
            'editore_username': username,
        })

    from .models import Recensione
    from .forms import RecensioneForm
    import datetime

    # Eventi prenotati con info recensione e conclusione
    eventi_prenotati_info = []
    for evento in eventi_prenotati:
        # Evento concluso se la data è passata
        data_evento = evento.data if evento.data else (evento.disponibilita.data if evento.disponibilita else None)
        concluso = data_evento and data_evento < datetime.date.today()
        # Recensione utente per questo evento
        recensione = Recensione.objects.filter(utente=request.user, firmacopie=evento).first()
        eventi_prenotati_info.append({
            'evento': evento,
            'concluso': concluso,
            'recensione': recensione,
        })

    # Gestione recensioni
    recensione_form = None
    if request.method == 'POST':
        evento_id = request.POST.get('evento_id')
        evento = FirmaCopie.objects.get(id=evento_id)
        if 'lascia_recensione' in request.POST:
            recensione_form = RecensioneForm()
            # Mostra form per lasciare recensione
        elif 'modifica_recensione' in request.POST:
            recensione = Recensione.objects.filter(utente=request.user, firmacopie=evento).first()
            recensione_form = RecensioneForm(instance=recensione)
        elif 'elimina_recensione' in request.POST:
            Recensione.objects.filter(utente=request.user, firmacopie=evento).delete()
            messages.success(request, 'Recensione eliminata!')
            return redirect('home_utente')
        elif 'salva_recensione' in request.POST:
            recensione = Recensione.objects.filter(utente=request.user, firmacopie=evento).first()
            if recensione:
                recensione_form = RecensioneForm(request.POST, instance=recensione)
            else:
                recensione_form = RecensioneForm(request.POST)
            if recensione_form.is_valid():
                rec = recensione_form.save(commit=False)
                rec.utente = request.user
                rec.firmacopie = evento
                rec.save()
                messages.success(request, 'Recensione salvata!')
                return redirect('home_utente')
            else:
                messages.error(request, 'Errore nella recensione.')

    return render(request, 'comicon/home_utente.html', {
        'eventi_info': eventi_info,
        'eventi_prenotati_info': eventi_prenotati_info,
        'recensione_form': recensione_form,
        'case_prodotti': case_prodotti,
        'messages': messages.get_messages(request),
    })
def registrazione_view(request):
    if request.method == 'POST':
        form = RegistrazioneForm(request.POST)
        if form.is_valid():
            utente = form.save(commit=False)
            utente.ruolo = form.cleaned_data['ruolo']
            utente.nome = form.cleaned_data['nome']
            utente.cognome = form.cleaned_data['cognome']
            utente.email = form.cleaned_data['email']
            utente.save()
            login(request, utente)
            messages.success(request, 'Registrazione avvenuta con successo!')
            return redirect('home_redirect')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrazioneForm()
    return render(request, 'comicon/registrazione.html', {'form': form})



@login_required
def home_autore_view(request):
    if request.user.ruolo != 'autore':
        return render(request, 'comicon/errore_ruolo.html', {'messaggio': 'Accesso non consentito: ruolo non valido per questa pagina.'})
    try:
        autore = Autore.objects.get(utente=request.user)
    except Autore.DoesNotExist:
        return render(request, 'comicon/errore_ruolo.html', {'messaggio': 'Profilo autore non trovato. Contatta l\'amministratore per la creazione del profilo.'})

    fumetto = autore.opera_principale if hasattr(autore, 'opera_principale') else None
    disponibilita = Disponibilita.objects.filter(autore=autore)
    
    # ✅ OTTIMIZZAZIONE: Fetch con select_related per evitare N+1 queries
    firmacopie_list = FirmaCopie.objects.filter(autore=autore).select_related(
        'autore', 'disponibilita', 'stand'
    )
    
    # ✅ OTTIMIZZAZIONE: Annotate per conteggio prenotazioni in una sola query
    firmacopie_list = firmacopie_list.annotate(
        posti_occupati=Count('prenotazioni')
    )

    fumetto_form = FumettoForm(instance=fumetto) if fumetto else FumettoForm()
    autore_form = AutoreForm(instance=autore)
    DisponibilitaFormSet = modelformset_factory(Disponibilita, form=DisponibilitaForm, extra=1, can_delete=True)
    disponibilita_formset = DisponibilitaFormSet(queryset=Disponibilita.objects.filter(autore=autore))
    show_fumetto_form = False

    # Calcolo info firmacopie con posti disponibili usando annotate
    firmacopie_info = []
    for fc in firmacopie_list:
        posti_totali = fc.stand.totale_persone if fc.stand and hasattr(fc.stand, 'totale_persone') else 0
        posti_disponibili = posti_totali - fc.posti_occupati  # Usa il valore annotated
        
        firmacopie_info.append({
            'data': fc.disponibilita.data if fc.disponibilita else None,
            'orario': fc.disponibilita.orario if fc.disponibilita else None,
            'stand': fc.stand,
            'casa_editrice': fc.casa_editrice,
            'autore': fc.autore,
            'posti_disponibili': posti_disponibili
        })

    if request.method == 'POST':
        if 'add_fumetto' in request.POST:
            fumetto_form = FumettoForm(request.POST)
            if fumetto_form.is_valid():
                nuovo_fumetto = fumetto_form.save(commit=False)
                # Usa la casa editrice selezionata nel form
                nuovo_fumetto.casa_editrice = fumetto_form.cleaned_data['casa_editrice']
                nuovo_fumetto.save()
                autore.opera_principale = nuovo_fumetto
                autore.save()
                if autore.opera_principale_id:
                    messages.success(request, "Fumetto di punta aggiunto correttamente!")
                else:
                    messages.error(request, "Errore: il fumetto di punta non è stato associato correttamente.")
                return redirect('home_autore')
        elif 'salva_fumetto' in request.POST:
            fumetto_form = FumettoForm(request.POST, instance=fumetto)
            if fumetto_form.is_valid():
                fumetto_mod = fumetto_form.save(commit=False)
                fumetto_mod.casa_editrice = fumetto_form.cleaned_data['casa_editrice']
                fumetto_mod.save()
                autore.opera_principale = fumetto_mod
                autore.save()
                if autore.opera_principale_id:
                    messages.success(request, "Fumetto di punta aggiornato correttamente!")
                else:
                    messages.error(request, "Errore: il fumetto di punta non è stato aggiornato correttamente.")
                return redirect('home_autore')
            else:
                show_fumetto_form = True
        elif 'modifica_fumetto' in request.POST:
            show_fumetto_form = True
        elif 'elimina_fumetto' in request.POST:
            if fumetto:
                fumetto.delete()
                autore.opera_principale = None
                autore.save()
                messages.success(request, "Fumetto di punta eliminato!")
                return redirect('home_autore')
        elif 'aggiungi_disponibilita' in request.POST or 'form-TOTAL_FORMS' in request.POST:
            disponibilita_formset = DisponibilitaFormSet(request.POST, queryset=Disponibilita.objects.filter(autore=autore))
            if disponibilita_formset.is_valid():
                instances = disponibilita_formset.save(commit=False)
                for instance in instances:
                    instance.autore = autore
                    instance.save()
                for obj in disponibilita_formset.deleted_objects:
                    obj.delete()
                messages.success(request, "Disponibilità aggiornata!")
                return redirect('home_autore')

    return render(request, 'comicon/home_autore.html', {
        'fumetto': fumetto,
        'fumetto_form': fumetto_form,
        'autore_form': autore_form,
        'disponibilita': disponibilita,
        'disponibilita_formset': disponibilita_formset,
        'show_fumetto_form': show_fumetto_form,
        'firmacopie_info': firmacopie_info,
        'messages': messages.get_messages(request),
    })

@login_required
def elimina_disponibilita(request, disp_id):
    disp = get_object_or_404(Disponibilita, id=disp_id, autore__utente=request.user)
    disp.delete()
    messages.success(request, "Disponibilità eliminata.")
    return redirect('home_autore')

@login_required
@ensure_csrf_cookie
def home_editore_view(request):
    if request.user.ruolo != 'editore':
        return render(request, 'comicon/errore_ruolo.html', {'messaggio': 'Accesso non consentito: ruolo non valido per questa pagina.'})
    casa_editrice = request.user.casa_editrice
    # Mostra solo autori che hanno come opera principale un fumetto associato a questa casa editrice
    autori = Autore.objects.filter(opera_principale__casa_editrice=casa_editrice).distinct()
    prodotti = Prodotto.objects.filter(casa_editrice=casa_editrice)
    
    # ✅ OTTIMIZZAZIONE: Fetch con select_related per evitare N+1 queries
    eventi = FirmaCopie.objects.filter(autore__in=autori).select_related(
        'autore', 'autore__utente', 'stand', 'disponibilita'
    )
    
    # ✅ OTTIMIZZAZIONE: Annotate per conteggio prenotazioni in una sola query
    eventi = eventi.annotate(
        posti_occupati=Count('prenotazioni')
    )

    prodotto_modifica = None
    prodotto_form = ProdottoForm()
    if request.method == 'POST':
        if 'modifica_prodotto_id' in request.POST:
            prodotto_modifica = get_object_or_404(Prodotto, id=request.POST['modifica_prodotto_id'], casa_editrice=casa_editrice)
            prodotto_form = ProdottoForm(instance=prodotto_modifica)
        elif 'salva_modifica_prodotto' in request.POST:
            prodotto_modifica = get_object_or_404(Prodotto, id=request.POST['prodotto_id'], casa_editrice=casa_editrice)
            prodotto_form = ProdottoForm(request.POST, instance=prodotto_modifica)
            if prodotto_form.is_valid():
                prodotto_form.save()
                messages.success(request, "Prodotto modificato con successo.")
                return redirect('home_editore')
        elif 'aggiungi_prodotto' in request.POST:
            prodotto_form = ProdottoForm(request.POST)
            if prodotto_form.is_valid():
                prodotto = prodotto_form.save(commit=False)
                prodotto.casa_editrice = casa_editrice
                prodotto.save()
                messages.success(request, f"Prodotto '{prodotto.nome}' aggiunto con successo.")
                return redirect('home_editore')
    
    # ✅ Prepara info eventi con posti
    eventi_dettaglio = []
    for evento in eventi:
        stand = evento.stand
        posti_totali = getattr(stand, 'totale_persone', 0) if stand else 0
        posti_disponibili = posti_totali - evento.posti_occupati  # Usa il valore annotated
        
        eventi_dettaglio.append({
            'evento': evento,
            'stand': stand,
            'posti_occupati': evento.posti_occupati,
            'posti_totali': posti_totali,
            'posti_disponibili': posti_disponibili,
        })
    
    return render(request, 'comicon/home_editore.html', {
        'autori': autori,
        'prodotti': prodotti,
        'prodotto_modifica': prodotto_modifica,
        'prodotto_form': prodotto_form,
        'eventi_dettaglio': eventi_dettaglio,
        'messages': messages.get_messages(request),
    })



def crea_aggiorna_profilo_autore(request):
    try:
        autore = request.user.autore
        form = AutoreForm(instance=autore)
    except Autore.DoesNotExist:
        autore = None
        form = AutoreForm()

    if request.method == 'POST':
        form = AutoreForm(request.POST, instance=autore)
        if form.is_valid():
            nuovo_autore = form.save(commit=False)
            nuovo_autore.user = request.user
            nuovo_autore.save()
            return redirect('home_autore')  # nome url di home autore

    return render(request, 'crea_aggiorna_profilo_autore.html', {'form': form})

@login_required
@require_POST
def elimina_autore_editore(request, autore_id):
    if request.user.ruolo != 'editore':
        return render(request, 'comicon/errore_ruolo.html', {'messaggio': 'Accesso non consentito.'})
    casa_editrice = request.user.casa_editrice
    autore = get_object_or_404(Autore, id=autore_id, casa_editrice=casa_editrice)
    autore.casa_editrice = None
    autore.save()
    messages.success(request, f"Autore {autore} rimosso dalla tua lista.")
    return redirect('home_editore')

@login_required
def elimina_prodotto(request, prodotto_id):
    prodotto = get_object_or_404(Prodotto, id=prodotto_id, casa_editrice=request.user.casa_editrice)
    if request.method == 'POST':
        prodotto.delete()
        messages.success(request, "Prodotto eliminato con successo.")
        return redirect('home_editore')
    return render(request, 'comicon/conferma_elimina_prodotto.html', {'prodotto': prodotto})

@csrf_exempt
@require_GET
@login_required
def ajax_casa_editrice_autore(request):
    autore_id = request.GET.get('autore_id')
    if not autore_id:
        return JsonResponse({'error': 'Missing autore_id'}, status=400)
    try:
        autore = Autore.objects.get(pk=autore_id)
        casa_editrice_id = autore.casa_editrice.id if autore.casa_editrice else None
    except Autore.DoesNotExist:
        casa_editrice_id = None
    return JsonResponse({'casa_editrice_id': casa_editrice_id})

@login_required
def modifica_prodotto(request, prodotto_id):
    prodotto = get_object_or_404(Prodotto, id=prodotto_id, casa_editrice=request.user.casa_editrice)
    if request.method == 'POST':
        form = ProdottoForm(request.POST, instance=prodotto)
        if form.is_valid():
            form.save()
            messages.success(request, "Prodotto modificato con successo.")
            return redirect('home_editore')
    else:
        form = ProdottoForm(instance=prodotto)
    return render(request, 'comicon/modifica_prodotto.html', {'form': form, 'prodotto': prodotto})
