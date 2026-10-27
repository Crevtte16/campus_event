"""
CAMPUS EVENT - API REST Flask
Gestion d'événements universitaires
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
#ilyes
app = Flask(__name__)
CORS(app)  # Permet au frontend (index.html) d'accéder à l'API sans blocage CORS

# ==============================================================================
# DONNÉES EN MÉMOIRE
# ==============================================================================

students = [
    {"id": 1, "first_name": "Stephen", "last_name": "Akugbe", "email": "stephen.akugbe@univ.fr", "major": "Informatique"},
    {"id": 2, "first_name": "Alice", "last_name": "Dupont", "email": "alice.dupont@univ.fr", "major": "Systèmes d'Information"},
    {"id": 3, "first_name": "Bob", "last_name": "Martin", "email": "bob.martin@univ.fr", "major": "Cybersécurité"},
    {"id": 4, "first_name": "Emma", "last_name": "Bernard", "email": "emma.bernard@univ.fr", "major": "Data Science"}
]

events = [
    {
        "id": 1,
        "title": "Forum Entreprises & Stages",
        "description": "Rencontre annuelle avec plus de 40 entreprises partenaires pour stages et alternances.",
        "date": "2026-11-15 09:30",
        "location": "Grand Hall - Bâtiment A",
        "capacity": 2  # Petite capacité pour tester facilement la règle d'événement complet
    },
    {
        "id": 2,
        "title": "Conférence IA & Systèmes d'Information",
        "description": "Les nouvelles architectures logicielles à l'ère de l'intelligence artificielle.",
        "date": "2026-11-20 14:00",
        "location": "Amphithéâtre Turing",
        "capacity": 50
    },
    {
        "id": 3,
        "title": "Atelier Hackathon & Sécurité Web",
        "description": "Atelier pratique sur les failles OWASP et la sécurisation des API REST.",
        "date": "2026-11-28 10:00",
        "location": "Salle Réseau 204",
        "capacity": 15
    }
]

registrations = []
registration_counter = 1

# ==============================================================================
# FONCTIONS UTILITAIRES MÉTIER
# ==============================================================================

def get_event_available_seats(event_id):
    """Calcule le nombre de places restantes pour un événement donné."""
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return 0
    # On compte les inscriptions actives (pending ou accepted)
    active_regs = [r for r in registrations if r["event_id"] == event_id and r["status"] in ["pending", "accepted"]]
    return max(0, event["capacity"] - len(active_regs))

def enrich_event_with_seats(event):
    """Ajoute le nombre de places disponibles et le nombre d'inscrits à l'objet événement."""
    ev = dict(event)
    active_regs = [r for r in registrations if r["event_id"] == event["id"] and r["status"] in ["pending", "accepted"]]
    ev["registered_count"] = len(active_regs)
    ev["available_seats"] = max(0, event["capacity"] - len(active_regs))
    return ev

# ==============================================================================
# ENDPOINTS REST
# ==============================================================================

@app.route("/", methods=["GET"])
def home():
    """Point d'accueil et documentation rapide."""
    return jsonify({
        "service": "CAMPUS EVENT API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "GET /events": "Liste de tous les événements",
            "GET /events/<id>": "Détails d'un événement",
            "GET /students": "Liste des étudiants",
            "GET /registrations": "Liste de toutes les inscriptions",
            "GET /registrations/<id>": "Détail d'une inscription",
            "POST /registrations": "Créer une inscription",
            "PATCH /registrations/<id>": "Mettre à jour le statut d'une inscription"
        }
    }), 200

# ------------------------------------------------------------------------------
# 1. ÉVÉNEMENTS
# ------------------------------------------------------------------------------

@app.route("/events", methods=["GET"])
def get_events():
    """Consulter tous les événements avec places disponibles."""
    enriched = [enrich_event_with_seats(e) for e in events]
    return jsonify(enriched), 200

@app.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    """Consulter un événement précis."""
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Événement introuvable"}), 404
    return jsonify(enrich_event_with_seats(event)), 200

# ------------------------------------------------------------------------------
# 2. ÉTUDIANTS
# ------------------------------------------------------------------------------

@app.route("/students", methods=["GET"])
def get_students():
    """Consulter la liste de tous les étudiants."""
    return jsonify(students), 200

@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    """Consulter un étudiant précis."""
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"error": "Étudiant introuvable"}), 404
    return jsonify(student), 200

# ------------------------------------------------------------------------------
# 3. INSCRIPTIONS
# ------------------------------------------------------------------------------

@app.route("/registrations", methods=["GET"])
def get_registrations():
    """Consulter toutes les inscriptions."""
    return jsonify(registrations), 200

@app.route("/registrations/<int:reg_id>", methods=["GET"])
def get_registration(reg_id):
    """Consulter une inscription précise."""
    registration = next((r for r in registrations if r["id"] == reg_id), None)
    if not registration:
        return jsonify({"error": "Inscription introuvable"}), 404
    return jsonify(registration), 200

@app.route("/registrations", methods=["POST"])
def create_registration():
    """
    Créer une nouvelle inscription.
    Règles métier :
    - 400 Bad Request si JSON absent ou champs obligatoires absents
    - 404 Not Found si l'étudiant n'existe pas
    - 404 Not Found si l'événement n'existe pas
    - 409 Conflict si l'étudiant est déjà inscrit à cet événement
    - 409 Conflict si l'événement est complet
    - 201 Created si inscription réussie (statut: 'pending')
    """
    global registration_counter

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Corps de requête JSON manquant ou invalide"}), 400

    # Règle : Champs obligatoires absents
    if "student_id" not in data or "event_id" not in data:
        return jsonify({"error": "Champs obligatoires absents : 'student_id' et 'event_id' requis"}), 400

    student_id = data.get("student_id")
    event_id = data.get("event_id")

    # Règle : Étudiant inexistant
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return jsonify({"error": f"Étudiant avec l'id {student_id} introuvable"}), 404

    # Règle : Événement inexistant
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": f"Événement avec l'id {event_id} introuvable"}), 404

    # Règle : Double inscription
    existing = next((r for r in registrations if r["student_id"] == student_id and r["event_id"] == event_id and r["status"] != "rejected"), None)
    if existing:
        return jsonify({"error": "Double inscription détectée : l'étudiant a déjà une inscription active pour cet événement"}), 409

    # Règle : Événement complet
    available_seats = get_event_available_seats(event_id)
    if available_seats <= 0:
        return jsonify({
            "error": "Événement complet",
            "message": "La capacité maximale a été atteinte. Inscription refusée."
        }), 409

    # Règle : Création réussie
    new_registration = {
        "id": registration_counter,
        "student_id": student_id,
        "student_name": f"{student['first_name']} {student['last_name']}",
        "event_id": event_id,
        "event_title": event["title"],
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    registrations.append(new_registration)
    registration_counter += 1

    return jsonify({
        "message": "Inscription enregistrée avec succès",
        "registration": new_registration
    }), 201

@app.route("/registrations/<int:reg_id>", methods=["PATCH"])
def update_registration_status(reg_id):
    """
    Modifier le statut d'une inscription.
    Statuts acceptés : 'pending', 'accepted', 'rejected', 'waitlisted'.
    """
    registration = next((r for r in registrations if r["id"] == reg_id), None)
    if not registration:
        return jsonify({"error": "Inscription introuvable"}), 404

    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return jsonify({"error": "Champ 'status' obligatoire requis"}), 400

    new_status = data.get("status")
    allowed_statuses = ["pending", "accepted", "rejected", "waitlisted"]
    if new_status not in allowed_statuses:
        return jsonify({
            "error": f"Statut invalide. Statuts autorisés : {', '.join(allowed_statuses)}"
        }), 400

    registration["status"] = new_status
    registration["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "message": "Statut de l'inscription mis à jour avec succès",
        "registration": registration
    }), 200

# ==============================================================================
# POINT D'ENTRÉE DU SERVEUR
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" Démarrage du serveur CAMPUS EVENT (API REST Flask)")
    print(" Adresse : http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
