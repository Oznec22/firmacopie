# Generated migration to optimize FirmaCopie and Prenotazione models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comicon', '0023_delete_evento'),
    ]

    operations = [
        # Rimuovere RegistrazioneEvento
        migrations.DeleteModel(
            name='RegistrazioneEvento',
        ),
        
        # Rimuovere campi ridondanti da FirmaCopie
        migrations.RemoveField(
            model_name='firmacopie',
            name='casa_editrice',
        ),
        migrations.RemoveField(
            model_name='firmacopie',
            name='data',
        ),
        migrations.RemoveField(
            model_name='firmacopie',
            name='ora',
        ),
        
        # Modificare FirmaCopie per rimuovere default da disponibilita
        migrations.AlterField(
            model_name='firmacopie',
            name='disponibilita',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventi_firmacopie', to='comicon.disponibilita'),
        ),
        migrations.AlterField(
            model_name='firmacopie',
            name='autore',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventi_firmacopie', to='comicon.autore'),
        ),
        migrations.AlterField(
            model_name='firmacopie',
            name='stand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventi_firmacopie', to='comicon.stand'),
        ),
        
        # Aggiungere unique_together a FirmaCopie
        migrations.AlterUniqueTogether(
            name='firmacopie',
            unique_together={('disponibilita', 'stand')},
        ),
        
        # Aggiungere related_name a Prenotazione
        migrations.AlterField(
            model_name='prenotazione',
            name='firmacopie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prenotazioni', to='comicon.firmacopie'),
        ),
        migrations.AlterField(
            model_name='prenotazione',
            name='utente',
            field=models.ForeignKey(limit_choices_to={'ruolo': 'utente'}, on_delete=django.db.models.deletion.CASCADE, related_name='prenotazioni', to='comicon.utente'),
        ),
        
        # Aggiungere unique_together a Prenotazione
        migrations.AlterUniqueTogether(
            name='prenotazione',
            unique_together={('utente', 'firmacopie')},
        ),
    ]
