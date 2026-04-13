# Generated migration to delete Evento model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comicon', '0022_remove_evento_posti_disponibili_remove_firmacopie_posti_disponibili'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Evento',
        ),
    ]
