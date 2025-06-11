import requests

API_URL = "http://localhost:5000/ask-with-memory"

contenu = input("Que veux-tu enseigner à iAngel ?\n> ")

try:
    response = requests.post(API_URL, json={"content": contenu})
    response.raise_for_status()
    print("✅ Réponse :", response.json())
except requests.exceptions.HTTPError as http_err:
    print(f"❌ HTTP Error: {http_err}")
    print("Contenu brut:", response.text)
except Exception as err:
    print(f"❌ Autre erreur : {err}")
