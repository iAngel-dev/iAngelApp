# iangel_watchdog.py
import json
import os
import time
import threading
from datetime import datetime

TASK_FILE = "tasks.json"
_task_lock = threading.Lock() # Le même principe de verrou

def execute_action(action: dict):
    """Exécute l'action définie dans une tâche."""
    action_type = action.get("type")
    message = action.get("message", "Action de rappel sans message.")
    
    if action_type == "log_message" or action_type == "print":
        print(f"🔔 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ACTION DÉCLENCHÉE : {message}")
    # On pourrait ajouter d'autres types d'actions ici : 'play_sound', 'call_api', etc.

def main_loop():
    print("🕰️  iAngel Watchdog démarré. Surveillance de tasks.json...")
    while True:
        try:
            with _task_lock:
                if not os.path.exists(TASK_FILE):
                    time.sleep(1)
                    continue

                tasks_modified = False
                with open(TASK_FILE, 'r+', encoding='utf-8') as f:
                    tasks = json.load(f)
                    current_time = time.time()
                    
                    for task in tasks:
                        if not task.get("triggered") and current_time >= task.get("execution_time", float('inf')):
                            execute_action(task["action"])
                            task["triggered"] = True
                            tasks_modified = True
                    
                    if tasks_modified:
                        # On réécrit le fichier avec les tâches mises à jour
                        f.seek(0)
                        f.truncate()
                        json.dump(tasks, f, indent=2)

        except (json.JSONDecodeError, IOError) as e:
            print(f"Erreur de lecture/écriture du fichier de tâches : {e}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue dans le watchdog : {e}")

        time.sleep(1) # Le watchdog vérifie les tâches chaque seconde

if __name__ == "__main__":
    main_loop()