from django.core.management.base import BaseCommand
from comicon.models import Prenotazione, FirmaCopie

class Command(BaseCommand):
    help = 'Elimina tutte le prenotazioni con firmacopie non valido (mancante o cancellato)'

    def handle(self, *args, **options):
        # Trova prenotazioni con firmacopie mancante (firmacopie_id non valido)
        invalid_prenotazioni = Prenotazione.objects.filter(firmacopie__isnull=True)
        # Trova prenotazioni che puntano a una firmacopie che non esiste più
        orphaned_prenotazioni = Prenotazione.objects.exclude(firmacopie__in=FirmaCopie.objects.all())
        # Unisci i due queryset senza duplicati
        all_invalid = invalid_prenotazioni | orphaned_prenotazioni
        count = all_invalid.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Nessuna prenotazione non valida trovata.'))
            return
        all_invalid.delete()
        self.stdout.write(self.style.SUCCESS(f'Eliminate {count} prenotazioni non valide.'))
