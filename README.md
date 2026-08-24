# Comicon 2026 - Autograph & Event Management Portal

**Firmacopie** is a web platform designed for the integrated management of autograph sessions and meet-and-greets during Comicon 2026. The system allows users to book tickets for signing sessions, authors to manage their availability, and publishers to coordinate their artists and products.

---

## Features & User Guide

### 1. Home & Authentication
The landing page provides an overview of the event. Users can register and log in, choosing their specific **Role**:
* **User (Fan):** Wants to attend events and receive autographs.
* **Author:** Artists managing their schedule and signing sessions.
* **Publisher (Editore):** Publishing houses coordinating booths and authors.
Upon login, the system automatically redirects to a role-specific dashboard.

### 2. User Dashboard (Fans)
* Browse available signing sessions filtered by author or publisher.
* Check remaining seats for each booth.
* Click "Prenota" (Book) to generate and save a unique virtual ticket in the database.
* Leave a 1-5 star rating and a text review after attending an event.

### 3. Author Dashboard
* Set a flagship comic/work.
* Declare available days and time slots for booth presence.

### 4. Publisher Dashboard
* View associated authors.
* Add new products/comics to the catalog.
* Monitor booking trends for their events.

### 5. Admin Panel
Restricted access for administrators to manage pavilions, booths, and overall database maintenance.

---

## Test Accounts

You can test the platform's role-based access control using the following pre-configured accounts:

* **Private User (Fan)** | Username: `mario` | Password: `comicon!`
* **Author** | Username: `Oda` | Password: `comicon!`
* **Publisher** | Username: `mondadori` | Password: `comicon!`

---

## Project Structure

### Models (`models.py`)
* **Utente**: `username`, `password`, `email`, `ruolo`, `casa_editrice`
* **Autore**: `utente`, `opera_principale`, `giorni_disponibili`, `orari_disponibili`
* **Fumetto**: `titolo`, `prezzo`, `genere`, `casa_editrice`
* **Stand**: `padiglione`, `stallo`, `totale_persone`, `disponibilita`
* **FirmaCopie**: `autore`, `disponibilita`, `stand`, `posti_disponibili`
* **Prenotazione**: `utente`, `firmacopie`, `timestamp`
* **Recensione**: `utente`, `firmacopie`, `testo`, `voto`, `data`

### Core Views (`views.py`)
* `login_view` / `registrazione_view`
* `home_redirect_view` (Role-based routing)
* `home_utente_view` / `home_autore_view` / `home_editore_view`
* `prenota_annulla_evento`
* `ajax_casa_editrice_autore`

---

## Local Setup & Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
