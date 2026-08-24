# FIRMACOPIE - COMICON 2026 EVENT MANAGEMENT PORTAL

**Firmacopie** is a web platform designed for the integrated management of autograph sessions and meet-and-greets during Comicon 2026. The system allows users to book tickets for signing sessions, authors to manage their availability, and publishing houses to coordinate their artists and products.

---

## HOW TO USE THE SITE

### 1. HOME
Main page that welcomes the user with an overview of the event. From here it is possible to access the login and registration sections. After logging in, the system redirects the user to the specific dashboard based on their role.

### 2. REGISTRATION
Enter username, email, and password. It is crucial to choose the correct **role**:
* **User:** For those who want to participate and receive autographs.
* **Author:** For artists who need to manage their schedules.
* **Publisher:** For publishing houses coordinating booths and products.

### 3. LOGIN
Enter your credentials to access the reserved features. The system automatically recognizes whether you are a user, an author, or a publisher.

### 4. TICKET BOOKING (Users)
View the list of available signing sessions filtered by author or publisher. 
* You can see the remaining seats for each booth.
* By clicking on "Book", you will receive a unique virtual ticket saved in the database.

### 5. AUTHOR MANAGEMENT (Authors)
Authors can set their flagship comic and declare the days and time slots they will be present at the booths.

### 6. CATALOG MANAGEMENT (Publishers)
Publishers can view their associated authors, add new products to the catalog, and monitor the booking trends for their events.

### 7. REVIEWS
After attending an event, the user can leave a review with a text comment and a rating from 1 to 5 stars. It is possible to see the average reviews for each author.

### 8. ADMIN
Restricted access for administrators to manage pavilions, booths, and general database maintenance.

---

## TEST ACCOUNTS

To test the different portal features based on access permissions, you can use the following pre-configured accounts:

### PRIVATE USER (Fan)
* **Username:** `mario`
* **Password:** `comicon!`

### AUTHOR
* **Username:** `Oda`
* **Password:** `comicon!`

### PUBLISHER
* **Username:** `mondadori`
* **Password:** `comicon!`

---

## PROJECT STRUCTURE

### MODELS (`models.py`)
* **User**: `username`, `password`, `email`, `ruolo`, `casa_editrice`
* **Author**: `utente`, `opera_principale`, `giorni_disponibili`, `orari_disponibili`
* **Comic**: `titolo`, `prezzo`, `genere`, `casa_editrice`
* **Booth**: `padiglione`, `stallo`, `totale_persone`, `disponibilita`
* **FirmaCopie**: `autore`, `disponibilita`, `stand`, `posti_disponibili`
* **Booking**: `utente`, `firmacopie`, `timestamp`
* **Review**: `utente`, `firmacopie`, `testo`, `voto`, `data`

### VIEWS (`views.py`)
* `login_view` / `registrazione_view`
* `home_redirect_view` (role routing)
* `home_utente_view` / `home_autore_view` / `home_editore_view`
* `prenota_annulla_evento`
* `ajax_casa_editrice_autore`

---

## STARTUP INSTRUCTIONS

1. **Create the virtual environment:**
   `python -m venv .venv`

2. **Activate it:**
   `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)

3. **Install the packages:**
   `pip install django django-extensions`

4. **Run the migrations:**
   `python manage.py makemigrations`
   `python manage.py migrate`

5. **Start the server:**
   `python manage.py runserver`

---

**Author:** Mataluna Vincenzo  
**Course:** Databases  
**University:** Università degli Studi di Napoli Parthenope
