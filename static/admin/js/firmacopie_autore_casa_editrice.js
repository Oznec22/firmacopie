// Script per aggiornare la casa editrice in base all'autore selezionato nel form admin FirmaCopie
(function() {
    // Funzione per recuperare il token CSRF dal cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function aggiornaCasaEditrice() {
        var autoreSelect = document.getElementById('id_autore');
        var casaEditriceInput = document.getElementById('id_casa_editrice');
        if (!autoreSelect || !casaEditriceInput) return;
        var autoreId = autoreSelect.value;
        if (!autoreId) return;
        // Chiamata AJAX per recuperare la casa editrice dell'autore
        fetch('/admin/comicon/ajax/casa_editrice_autore/?autore_id=' + autoreId)
            .then(response => response.json())
            .then(data => {
                if (data.casa_editrice_id) {
                    // Seleziona la voce corretta nel menu a tendina
                    for (var i = 0; i < casaEditriceInput.options.length; i++) {
                        if (casaEditriceInput.options[i].value == data.casa_editrice_id) {
                            casaEditriceInput.selectedIndex = i;
                            break;
                        }
                    }
                    // Rendi il campo solo readonly e grigio, ma non disabilitato (così viene inviato nel form)
                    casaEditriceInput.readOnly = true;
                    casaEditriceInput.style.background = '#eee';
                } else {
                    casaEditriceInput.selectedIndex = 0;
                    casaEditriceInput.readOnly = false;
                    casaEditriceInput.style.background = '';
                }
            });
    }
    var autoreSelect = document.getElementById('id_autore');
    if (autoreSelect) {
        autoreSelect.addEventListener('change', aggiornaCasaEditrice);
        aggiornaCasaEditrice();
    }
    // Imposta sempre disabled anche al caricamento
    var casaEditriceInput = document.getElementById('id_casa_editrice');
    if (casaEditriceInput) {
        casaEditriceInput.disabled = true;
        casaEditriceInput.style.background = '#eee';
    }
})();
