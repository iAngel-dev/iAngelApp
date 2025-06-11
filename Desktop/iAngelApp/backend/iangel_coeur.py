# ==============================================================================
# iAngel - Cœur Généraliste v4.0 (Phase 1: Apprentissage)
# Auteur : Votre nom (avec l'assistance de Gemini, Senior AI Engineer)
# Description : Version de lancement conçue pour la flexibilité et 
#               l'expérimentation ML. Le cœur agit comme un orchestrateur
#               d'outils et de modèles, sans personnalité pré-définie.
# ==============================================================================

# --- Imports ---
import os
import json
import sqlite3
import time
import re
import logging
import tutor_service
import threading
import pickle
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, g as flask_g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TASK_FILE = "tasks.json"
MODELS_DIR = "models"
PROFILES_DIR = "user_profiles"

# --- Verrou pour l'accès au fichier de tâches ---
_task_lock = threading.Lock()

# --- Classe: Moteur d'Apprentissage Local (INSF) ---
# La classe est conservée pour gérer les profils et logger les interactions.
class INSFLocalLearner:
    # ... (Le code de la classe reste le même que dans la v3.1)
    def __init__(self, profiles_dir):
        self._profiles_dir = profiles_dir
        self._users_data = {}
        if not os.path.exists(self._profiles_dir):
            os.makedirs(self._profiles_dir)
        self._load_all_profiles()
    def _get_profile_path(self, user_id: str) -> str:
        return os.path.join(self._profiles_dir, f"{user_id}_profile.json")
    def _load_all_profiles(self):
        for filename in os.listdir(self._profiles_dir):
            if filename.endswith("_profile.json"):
                user_id = filename.replace("_profile.json", "")
                try:
                    with open(self._get_profile_path(user_id), 'r', encoding='utf-8') as f:
                        self._users_data[user_id] = json.load(f)
                except Exception as e:
                    app.logger.error(f"Erreur chargement profil {user_id}: {e}")
    def _save_user_profile(self, user_id: str):
        if user_id not in self._users_data: return
        try:
            with open(self._get_profile_path(user_id), 'w', encoding='utf-8') as f:
                json.dump(self._users_data[user_id], f, indent=4)
        except IOError as e:
            app.logger.error(f"Erreur sauvegarde profil {user_id}: {e}")
    def create_or_load_user_profile(self, user_id: str) -> dict:
        if user_id in self._users_data:
            return self._users_data[user_id]
        profile_path = self._get_profile_path(user_id)
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    self._users_data[user_id] = profile
                    return profile
            except Exception: pass
        default_profile = {
            "user_id": user_id, "interaction_log": [],
            "creation_date": datetime.now().isoformat()
        }
        self._users_data[user_id] = default_profile
        self._save_user_profile(user_id)
        return default_profile
    def record_interaction(self, user_id: str, prompt: str, response: str, internal_state: dict):
        if user_id not in self._users_data: return
        profile = self._users_data[user_id]
        interaction = {
            "timestamp": datetime.now().isoformat(), "prompt": prompt,
            "response": response, "iangel_internal_state": internal_state
        }
        profile.setdefault("interaction_log", []).append(interaction)
        self._save_user_profile(user_id)

# --- Fonction de Planification de Tâches (pour le watchdog) ---
def schedule_task(description: str, delay_seconds: int, action: dict) -> bool:
    # ... (Le code reste le même que dans la v3.1)
    with _task_lock:
        tasks = []
        if os.path.exists(TASK_FILE):
            try:
                with open(TASK_FILE, 'r', encoding='utf-8') as f: tasks = json.load(f)
            except (json.JSONDecodeError, IOError): tasks = []
        new_task = {
            "id": f"task_{int(time.time())}", "description": description,
            "execution_time": time.time() + delay_seconds, "triggered": False, "action": action
        }
        tasks.append(new_task)
        try:
            temp_file = TASK_FILE + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f: json.dump(tasks, f, indent=2)
            os.replace(temp_file, TASK_FILE)
            app.logger.info(f"Tâche persistante planifiée: '{description}'")
            return True
        except IOError as e:
            app.logger.error(f"Erreur E/S lors de la planification de la tâche: {e}", exc_info=True)
            return False

# --- Initialisation de Flask et des Moteurs ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
limiter = Limiter(get_remote_address, app=app)
insf_learner = INSFLocalLearner(profiles_dir=PROFILES_DIR)
if not os.path.exists(MODELS_DIR): os.makedirs(MODELS_DIR)

# --- NOUVEAU : Chargement des modèles ML au démarrage ---
ml_models = {}
app.logger.info(f"Chargement des modèles ML depuis le dossier '{MODELS_DIR}'...")
for filename in os.listdir(MODELS_DIR):
    if filename.endswith(".pkl"):
        model_name = filename.replace(".pkl", "")
        try:
            with open(os.path.join(MODELS_DIR, filename), 'rb') as f:
                ml_models[model_name] = pickle.load(f)
            app.logger.info(f"  > Modèle '{model_name}' chargé avec succès.")
        except Exception as e:
            app.logger.error(f"  > ERREUR lors du chargement du modèle '{model_name}': {e}")
app.logger.info(f"{len(ml_models)} modèles ML sont prêts à être utilisés.")

# --- Décorateurs (inchangés) ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-KEY') == API_KEY: return f(*args, **kwargs)
        return jsonify({"erreur": "Accès non autorisé"}), 403
    return decorated_function

# --- NOUVELLE ROUTE : Le "Bac à Sable" ML ---
@app.route("/predict/<model_name>", methods=['POST'])
@require_api_key
def predict(model_name: str):
    """
    Endpoint universel pour tester n'importe quel modèle ML chargé.
    Attend un JSON: {"features": [[...]]}
    """
    if model_name not in ml_models:
        return jsonify({"erreur": f"Modèle '{model_name}' non trouvé ou non chargé."}), 404
    
    data = request.get_json()
    if not data or "features" not in data:
        return jsonify({"erreur": "Le corps de la requête doit contenir un champ 'features'."}), 400

    features = data["features"]
    model = ml_models[model_name]

    try:
        prediction = model.predict(features)
        # Convertir la prédiction en une liste standard si c'est un array numpy
        if hasattr(prediction, 'tolist'):
            prediction = prediction.tolist()
        return jsonify({"model_used": model_name, "prediction": prediction})
    except Exception as e:
        app.logger.error(f"Erreur de prédiction avec le modèle '{model_name}': {e}", exc_info=True)
        return jsonify({"erreur": f"Erreur lors de la prédiction: {e}"}), 500

# --- ROUTE /ask : Le Distributeur de Commandes ---
@app.route("/ask", methods=['POST'])
@require_api_key
def ask_iangel():
    """
    Reçoit toutes les demandes et les distribue à l'outil approprié.
    C'est le point d'entrée principal.
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    prompt = data.get("prompt", "").strip()

    if not user_id or not prompt:
        return jsonify({"erreur": "user_id et prompt sont requis."}), 400

    insf_learner.create_or_load_user_profile(user_id)
    response_text = ""
    iangel_state = {"response_mode": "inconnu", "reason": "non analysé"}
    prompt_lower = prompt.lower()

    # 1. Triage des commandes
    if prompt_lower.startswith("rappel"):
        reminder_pattern = r"rappel(?:le-moi)? dans (\d+)\s(minute|minutes|seconde|secondes|heure|heures)\s(?:de|d'|pour)\s(.*)"
        match = re.search(reminder_pattern, prompt, re.IGNORECASE)
        if match:
            quantity, unit, task = map(str.strip, match.groups())
            delay = int(quantity)
            if "minute" in unit: delay *= 60
            elif "heure" in unit: delay *= 3600
            
            action = {"type": "log_message", "message": f"RAPPEL pour {user_id}: {task}"}
            schedule_task(description=task, delay_seconds=delay, action=action)
            
            response_text = f"C'est noté. Rappel programmé pour '{task}'."
            iangel_state = {"response_mode": "planification", "reason": "Commande de rappel reconnue."}
        else:
            response_text = "Je vois que vous voulez un rappel, mais je n'ai pas compris le format. Essayez 'rappel moi dans 5 minutes de ...'"
            iangel_state = {"response_mode": "clarification_rappel", "reason": "Format de rappel non reconnu."}
    
    # 2. On ajoutera ici d'autres commandes : "analyse url...", "résume ce texte...", etc.

    # 3. Comportement par défaut : Déléguer au tuteur externe    
    else        :
        # On prépare une instruction claire pour notre tuteur expert
        system_prompt = "Tu es un assistant IA factuel, neutre et concis. Réponds directement à la question suivante de l'utilisateur."
                # On appelle le service tuteur
        response_text = tutor_service.call_gemini_tutor(prompt)

        iangel_state = {
            "response_mode": "tutorat_externe",
            "reason": "Aucune commande interne reconnue, la question a été déléguée au tuteur Gemini.",
            "tutor_used": "gemini-1.5-flash"
        }

    # Journalisation de l'interaction
    insf_learner.record_interaction(user_id, prompt, response_text, iangel_state)
    return jsonify({"response": response_text, "iangel_state": iangel_state})

# --- Exécution ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
# === AJOUT Sol : Intégration mémoire + apprentissage INSF ===

@app.route("/ask-with-memory", methods=["POST"])
@require_api_key
def ask_with_memory():
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    contenu = data.get("content", "").strip()
    if not contenu:
        return jsonify({"erreur": "Contenu manquant."}), 400

    capsule = {
        "uuid": str(uuid.uuid4()),
        "date": datetime.now().isoformat(),
        "theme": "général",
        "resume": contenu[:150] + "..." if len(contenu) > 150 else contenu,
        "contenu": contenu
    }
    try:
        if os.path.exists("memoire.json"):
            with open("memoire.json", "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(capsule)
        with open("memoire.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        insf_learner.record_interaction(user_id, contenu, "Mémoire ajoutée", {"type": "memoire_integration"})
        return jsonify({"message": "Connaissance intégrée", "id": capsule["uuid"]})
    except Exception as e:
        return jsonify({"erreur": f"Échec intégration: {str(e)}"}), 500
