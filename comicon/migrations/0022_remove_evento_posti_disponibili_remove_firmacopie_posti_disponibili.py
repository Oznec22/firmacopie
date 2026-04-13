# Generated migration to remove posti_disponibili field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comicon', '0021_recensione'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evento',
            name='posti_disponibili',
        ),
        migrations.RemoveField(
            model_name='firmacopie',
            name='posti_disponibili',
        ),
    ]
