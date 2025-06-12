import sys
import time
import json
import random


def run_task(task_desc: str):
    """Simule l'exécution d'une tâche et son auto-évaluation."""
    print(f"iAngel_coeur: Focusing on task -> {task_desc}")
    start_time = time.time()

    # Simuler le travail
    time.sleep(random.randint(2, 5))

    # Simuler des points de stress internes
    internal_stress_points = []
    if random.random() < 0.2:
        error_message = "API externe a retourné une erreur 503."
        internal_stress_points.append(error_message)
        task_output = f"Failed to execute task: {task_desc}. Reason: {error_message}"
    else:
        task_output = f"Successfully executed task: {task_desc}"

    end_time = time.time()
    processing_time = int(end_time - start_time)

    result = {
        "output": task_output,
        "processing_time": processing_time,
        "internal_stress_points": internal_stress_points
    }

    print(json.dumps(result))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        task_description = sys.argv[1]
        run_task(task_description)
