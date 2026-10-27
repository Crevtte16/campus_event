# 🎓 CAMPUS EVENT — Système d'Information de Gestion d'Événements Universitaires

Projet académique réalisé pour le module **Introduction aux Systèmes d'Information**.

---

## 1. Description du Projet

**CAMPUS EVENT** est une solution complète permettant de centraliser et d'automatiser la gestion des événements universitaires (conférences, salons professionnels, hackathons, ateliers) et les inscriptions des étudiants.

Le système résout les problématiques d'incohérence, de gestion des jauges et de doubles inscriptions à travers une architecture 3-tiers découplée :
- **Frontend** : Interface Web dynamique en HTML5 / CSS3 / Vanilla JavaScript avec `fetch()`.
- **Backend / Logique Métier** : API REST développée en Python avec **Flask** et **Flask-CORS**.
- **Données** : Modèle de données centralisé en mémoire (dictionnaires Python).

---

## 2. Prérequis et Installation

### 2.1 Prérequis
- Python 3.8 ou supérieur installé sur votre machine.
- Gestionnaire de paquets `pip`.

### 2.2 Cloner le projet (si applicable)
```bash
git clone https://github.com/Osalumense/campus_event.git
cd campus_event
```

### 2.3 Installation des dépendances via `requirements.txt`
Installez les dépendances requises en exécutant la commande suivante :

```bash
pip install -r requirements.txt
```

*(Contient `Flask>=3.0.0` et `flask-cors>=4.0.0`)*.

---

## 3. Guide de Lancement Pas à Pas

### Étape 1 : Démarrer le serveur API Flask

Dans votre terminal, lancez le serveur backend :

```bash
python app.py
```

Le serveur démarre et écoute sur l'adresse locale :
👉 **`http://127.0.0.1:5000`**

Vous pouvez vérifier que l'API fonctionne en ouvrant cette URL dans votre navigateur ou via un terminal :
```bash
curl http://127.0.0.1:5000/
```

### Étape 2 : Lancer l'interface Web (Frontend)

Pendant que le serveur `python app.py` tourne :
1. Ouvrez le fichier **`index.html`** :
   - Par un simple **double-clic** sur le fichier `index.html` depuis votre explorateur de fichiers / Finder.
   - Ou avec l'extension VS Code **Live Server**.
   - Ou en ligne de commande avec :
     ```bash
     open index.html        # sur macOS
     # ou xdg-open index.html sur Linux / start index.html sur Windows
     ```
2. La page web se connecte automatiquement à l'API locale (`http://127.0.0.1:5000/events`) et affiche :
   - La liste dynamique des événements avec les **places restantes en direct**.
   - Le formulaire interactif permettant de sélectionner un étudiant et un événement pour s'inscrire.
   - Les messages de succès (`201 Created`) ou d'erreur métier (`400`, `404`, `409 Conflict` si complet ou doublon).

---

## 4. Tests de l'API avec Postman

Le projet inclut la collection officielle **`CAMPUS_EVENT.postman_collection.json`** préconfigurée avec les **10 tests obligatoires** et leurs assertions automatiques :

1. Ouvrez **Postman**.
2. Cliquez sur **Import** et sélectionnez le fichier `CAMPUS_EVENT.postman_collection.json`.
3. Cliquez avec le bouton droit sur la collection importée $\rightarrow$ **Run collection** $\rightarrow$ **Run CAMPUS EVENT — API Tests**.
4. Les 10 requêtes s'exécutent successivement et valident les statuts HTTP attendus (`200`, `201`, `400`, `404`, `409`).

---

## 5. Spécification des Endpoints REST

L'API respecte les principes fondamentaux de l'architecture REST :

| Méthode | Endpoint | Description | Code Succès |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Accueil et documentation des routes | `200 OK` |
| `GET` | `/events` | Liste de tous les événements avec places restantes | `200 OK` |
| `GET` | `/events/<id>` | Consultation d'un événement spécifique | `200 OK` |
| `GET` | `/students` | Liste de tous les étudiants enregistrés | `200 OK` |
| `GET` | `/students/<id>` | Consultation d'un étudiant spécifique | `200 OK` |
| `GET` | `/registrations` | Consultation de l'ensemble des inscriptions | `200 OK` |
| `GET` | `/registrations/<id>` | Consultation d'une inscription spécifique | `200 OK` |
| `POST` | `/registrations` | Création d'une nouvelle inscription | `201 Created` |
| `PATCH` | `/registrations/<id>` | Mise à jour du statut d'une inscription | `200 OK` |

---

## 6. Exemples de Requêtes (cURL / JSON)

### 6.1 Consulter la liste des événements
```bash
curl -X GET http://127.0.0.1:5000/events
```

### 6.2 Créer une inscription valide (`POST /registrations`)
```bash
curl -X POST http://127.0.0.1:5000/registrations \
     -H "Content-Type: application/json" \
     -d '{"student_id": 1, "event_id": 2}'
```
**Réponse attendue (`201 Created`) :**
```json
{
  "message": "Inscription enregistrée avec succès",
  "registration": {
    "created_at": "2026-10-27 14:00:00",
    "event_id": 2,
    "event_title": "Conférence IA & Systèmes d'Information",
    "id": 1,
    "status": "pending",
    "student_id": 1,
    "student_name": "Stephen Akugbe"
  }
}
```

### 6.3 Tester les erreurs métier
- **Champs obligatoires manquants (`400 Bad Request`) :**
  ```bash
  curl -X POST http://127.0.0.1:5000/registrations \
       -H "Content-Type: application/json" \
       -d '{"student_id": 1}'
  ```
- **Étudiant inexistant (`404 Not Found`) :**
  ```bash
  curl -X POST http://127.0.0.1:5000/registrations \
       -H "Content-Type: application/json" \
       -d '{"student_id": 999, "event_id": 1}'
  ```
- **Événement complet ou double inscription (`409 Conflict`) :**
  Tenter de s'inscrire une 2e fois au même événement, ou s'inscrire sur un événement dont la capacité maximale est atteinte.

### 6.4 Modifier le statut d'une inscription (`PATCH /registrations/<id>`)
```bash
curl -X PATCH http://127.0.0.1:5000/registrations/1 \
     -H "Content-Type: application/json" \
     -d '{"status": "accepted"}'
```

---

## 7. Structure du Répertoire GitHub

```text
campus_event/
├── app.py                               # API REST Flask
├── index.html                           # Interface Web (Frontend fetch())
├── rapport.pdf                          # Rapport académique complet
├── CAMPUS_EVENT.postman_collection.json # Collection Postman officielle (10 tests)
├── requirements.txt                     # Dépendances Python du projet
└── README.md                            # Guide d'installation et d'utilisation
```
