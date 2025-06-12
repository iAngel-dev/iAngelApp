import json
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ia_utils import merge_json_file, assess_task_with_ai, generate_stepwise_instructions

TASK_FILE = "tasks.json"
MEMORY_FILE = "memory.json"

class TaskHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(TASK_FILE):
            print("\nChange detected in tasks.json. Checking for pending tasks...")
            self.process_pending_task()

    def process_pending_task(self):
        try:
            with open(TASK_FILE, "r", encoding='utf-8') as f:
                tasks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        current_task = None
        for task in tasks:
            if task.get("status") == "pending":
                current_task = task
                break

        if not current_task:
            print("No pending tasks found.")
            return

        task_id = current_task.get("id")
        task_desc = current_task.get("description")
        print(f"--- Starting Task #{task_id}: {task_desc} ---")

        start_time = time.time()
        result = subprocess.run(
            ["python", "iangel_coeur.py", task_desc],
            capture_output=True, text=True, encoding='utf-8'
        )

        try:
            coeur_result = json.loads(result.stdout)
        except json.JSONDecodeError:
            coeur_result = {
                "output": "Failed to parse iangel_coeur output.",
                "processing_time": 0,
                "internal_stress_points": ["JSON Parse Error"]
            }

        print("Task complete. Asking AI Tutor for assessment...")
        assessment = assess_task_with_ai(
            task_desc=task_desc,
            task_output=coeur_result.get("output"),
            processing_time=coeur_result.get("processing_time")
        )

        all_stress_points = coeur_result.get("internal_stress_points", []) + assessment.get("stress_points", [])

        memory_entry = {
            "task_id": task_id,
            "description": task_desc,
            "output": coeur_result.get("output"),
            "lesson": assessment.get("step_tips"),
            "processing_time": coeur_result.get("processing_time"),
            "actual_difficulty": assessment.get("actual_difficulty"),
            "completion_quality": assessment.get("completion_quality"),
            "stress_points": all_stress_points
        }

        print(f"Saving new lesson to {MEMORY_FILE}...")
        merge_json_file(MEMORY_FILE, [memory_entry], key="task_id")

        print(f"Marking task #{task_id} as 'done'.")
        current_task["status"] = "done"
        current_task.update(assessment)
        current_task["stress_points"] = all_stress_points

        merge_json_file(TASK_FILE, [current_task], key="id")
        print(f"--- Task #{task_id} Finished ---")

        self.process_pending_task()

if __name__ == "__main__":
    handler = TaskHandler()
    print("Watchdog starting. Performing initial task check...")
    handler.process_pending_task()

    observer = Observer()
    observer.schedule(handler, path='.', recursive=False)
    observer.start()
    print(f"Watchdog is now monitoring {TASK_FILE} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
