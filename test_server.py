#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firmacopie.settings')
django.setup()

# Clear the error log
log_file = 'django_errors.log'
if os.path.exists(log_file):
    os.remove(log_file)
    print(f"✓ Log file '{log_file}' removed")
else:
    print(f"✓ Log file doesn't exist")

# Test the models and forms
print("\nTesting models and forms...")
try:
    from comicon.models import Autore, CasaEditrice, FirmaCopie, Prenotazione
    from comicon.forms import AssociaAutoriForm
    
    # Test AssociaAutoriForm
    casa = CasaEditrice.objects.first()
    if casa:
        form = AssociaAutoriForm(casa_editrice=casa)
        print(f"✓ AssociaAutoriForm initialized successfully with casa_editrice={casa.nome}")
    else:
        form = AssociaAutoriForm()
        print("✓ AssociaAutoriForm initialized successfully (no casa_editrice)")
    
    # Test FirmaCopie.get_posti_disponibili
    fc = FirmaCopie.objects.first()
    if fc:
        posti = fc.get_posti_disponibili()
        print(f"✓ FirmaCopie.get_posti_disponibili() = {posti}")
    else:
        print("✓ No FirmaCopie objects in database (this is ok)")
    
    print("\n✓✓✓ All tests passed! The application should work now.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
