# Generated migration to clean up ProdottoEditore and update Stand logic

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comicon', '0024_remove_redundant_fields_and_unify_models'),
    ]

    operations = [
        # Nota: ProdottoEditore rimane come modello deprecato per compatibilità
        # Il signal aggiornato per FirmaCopie verrà applicato automaticamente
        # CasaEditrice.__str__ è stato aggiornato per mostrare l'username
        migrations.RunPython(lambda apps, schema_editor: None),  # No database changes
    ]
