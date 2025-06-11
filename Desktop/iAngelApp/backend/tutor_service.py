# tutor_service.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement (votre clé API)
load_dotenv()

# Configuration de l'API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("AVERTISSEMENT : Clé API Gemini non trouvée. Le service tuteur sera désactivé.")
    genai.configure(api_key="INVALID_KEY") # Pour éviter un crash si la clé est manquante
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialisation du modèle que nous allons utiliser comme tuteur
# 'gemini-1.5-flash' est un excellent choix car il est très rapide et compétent.
model = genai.GenerativeModel('gemini-1.5-flash')

def call_gemini_tutor(prompt_pour_le_tuteur: str) -> str:
    """
    Fonction qui envoie un prompt à Gemini et retourne sa réponse textuelle.
    C'est notre ligne directe avec le tuteur expert.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "INVALID_KEY":
        return "Le service de tutorat externe n'est pas configuré (clé API manquante)."

    try:
        # On envoie la question au modèle
        response = model.generate_content(prompt_pour_le_tuteur)
        # On retourne uniquement le texte de la réponse
        return response.text
    except Exception as e:
        print(f"ERREUR lors de l'appel à l'API Gemini: {e}")
        return f"Désolée, une erreur technique m'empêche de contacter mon tuteur expert pour le moment."