import requests
import json
import datetime
import os

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"

messages = [
    {
        "role": "system", 
        "content": """Tu es un assistant CRM. Pour CHAQUE message, réponds UNIQUEMENT en JSON valide.
Si l'utilisateur veut l'heure              : {"action": "GET_TIME"}
Si l'utilisateur parle d'un client         : {"action": "SEARCH_CLIENT", "nom": "prénom nom"}
Pour toute autre réponse                   : {"action": "RESPOND", "message": "ta réponse"}"""
    }
]

print("=== Agent IA (Boucle ReAct & HITL) Démarré ===")

while True:
    user_input = input("\nVous: ")
    if user_input.lower() in ['quit', 'exit']:
        break

    # On convertit l'entrée de l'utilisateur en JSON pour être cohérent avec le format attendu
    messages.append({"role": "user", "content": json.dumps({"question": user_input})})

    max_iterations = 5
    iteration = 0
    tache_terminee = False

    # 🎯 À COMPLÉTER (6) : La boucle tourne tant qu'on n'a pas atteint la limite ET que la tâche n'est pas finie
    while iteration < max_iterations and not tache_terminee:
        iteration += 1
        print(f"  [Réflexion {iteration}/{max_iterations}]")

        payload = {"model": MODEL, "messages": messages, "stream": False, "format": "json"}
        try:
            response = requests.post(OLLAMA_URL, json=payload).json()
            raw = response["message"]["content"]
            messages.append({"role": "assistant", "content": raw})
        except Exception as e:
            print(f"  [⚠️ ERREUR API] {e}")
            break

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print(f"  [⚠️ ERREUR JSON] {raw}")
            break

        action = data.get("action", "RESPOND")

        if action == "GET_TIME":
            print(f"  [HITL] L'agent veut lire l'heure système.")
            confirmation = input("  Autoriser ? (o/n) : ")
            if confirmation.lower() != 'o':
                messages.append({"role": "user", "content": "[SYSTÈME] Action refusée par l'administrateur. Adapte ta réponse."})
                continue
            
            heure = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"  [OUTIL] Heure → {heure}")
            messages.append({"role": "user", "content": f"[SYSTÈME] Heure : {heure}. Continue ta réflexion."})

        elif action == "SEARCH_CLIENT":
            nom = data.get("nom", "")
            print(f"  [HITL] L'agent veut chercher '{nom}' dans la base clients.")
            confirmation = input("  Autoriser ? (o/n) : ")
            if confirmation.lower() != 'o':
                messages.append({"role": "user", "content": "[SYSTÈME] Action refusée par l'administrateur. Adapte ta réponse."})
                continue
            
            resultat = "Client non trouvé."
            if os.path.exists("clients.csv"):
                with open("clients.csv", "r") as f:
                    for ligne in f:
                        if nom.lower() in ligne.lower():
                            resultat = ligne.strip()
                            break
            print(f"  [OUTIL] RAG → {resultat}")
            messages.append({"role": "user", "content": f"[SYSTÈME] Résultat recherche : {resultat}. Continue ta réflexion."})

        elif action == "RESPOND":
            print(f"\nAgent: {data.get('message', '')}")
            # 🎯 À COMPLÉTER (7) : La tâche est terminée, on passe la variable à True pour sortir de la boucle while
            tache_terminee = True

    if not tache_terminee:
        print(f"\n[⚠️ TIMEOUT] L'agent n'a pas conclu en {max_iterations} itérations.")
