import openai
import json
import os

# --- Configuration ---
# Idéalement, à mettre dans un fichier .env
openai.api_key = "VOTRE_CLE_API_OPENAI_ICI"


def merge_json_file(filename: str, new_entries: list, key: str = "id"):
    """
    Fusionne de nouvelles entrées dans un fichier JSON.
    Met à jour les entrées existantes basées sur une clé unique, sinon les ajoute.
    """
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding='utf-8') as f:
                existing = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing = []
    else:
        existing = []

    existing_map = {str(entry.get(key)): entry for entry in existing if key in entry}

    for new_entry in new_entries:
        k = str(new_entry.get(key))
        if k in existing_map:
            existing_map[k].update(new_entry)
        else:
            existing_map[k] = new_entry

    merged = list(existing_map.values())
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    return merged


def assess_task_with_ai(task_desc: str, task_output: str, processing_time: int, model: str = "gpt-4"):
    """
    Évalue une tâche complétée en utilisant une IA pour l'analyse de sentiment/difficulté.
    """
    prompt = (
        f"Task description: {task_desc}\n"
        f"Task output: {task_output}\n\n"
        "Please assess the following:\n"
        "1. Rate actual difficulty (easy/medium/hard).\n"
        "2. Suggest how the steps could be more human, adaptive, and helpful for seniors or those with special needs.\n"
        "3. Rate the completion quality (high/medium/low).\n"
        "4. List any stress points (errors, confusion, user hesitations, etc.).\n"
        "Respond ONLY in JSON with keys: actual_difficulty, completion_quality, step_tips, stress_points."
    )
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert human-centered AI tutor."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_feedback_str = response.choices[0].message.content
        feedback = json.loads(ai_feedback_str)
    except Exception as e:
        print(f"Erreur lors de l'évaluation par l'IA : {e}")
        feedback = {
            "actual_difficulty": "unknown",
            "completion_quality": "unknown",
            "step_tips": "AI assessment failed.",
            "stress_points": [f"API Error: {str(e)}"]
        }

    feedback["processing_time"] = processing_time
    return feedback


def generate_stepwise_instructions(task_desc: str, model: str = "gpt-4"):
    """
    Génère des instructions simples, étape par étape, pour des utilisateurs ayant besoin d'assistance.
    """
    prompt = (
        f"Task: {task_desc}\n"
        "Break this task down into small, clear, step-by-step instructions. "
        "Use encouraging, friendly language suitable for someone who may be a senior or need extra help. "
        "Keep each step short and simple. "
        "Respond ONLY in JSON as a list of strings with the key 'steps'."
    )
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at accessible, stepwise instructions."},
                {"role": "user", "content": prompt}
            ]
        )
        steps = json.loads(response.choices[0].message.content).get("steps", [])
    except Exception as e:
        print(f"Erreur lors de la génération des étapes : {e}")
        steps = ["Could not generate steps for this task."]
    return steps
