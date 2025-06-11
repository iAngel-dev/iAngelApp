import requests

API_URL = "http://localhost:5000/ask-with-memory"

contenu = input("Que veux-tu enseigner à iAngel ?\n> ")

response = requests.post(API_URL, json={"content": contenu})

if response.ok:
    print("✅ Réponse :", response.json())
else:
    print("❌ Erreur :", response.text)
