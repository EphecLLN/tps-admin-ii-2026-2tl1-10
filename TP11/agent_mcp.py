# agent_mcp.py
import asyncio
import requests
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"

async def _appeler_outil(nom_outil: str, arguments: dict) -> str:
    params = StdioServerParameters(command="python3", args=["serveur_mcp.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(nom_outil, arguments)
            return result.content[0].text

def appeler_outil_mcp(nom_outil: str, **kwargs) -> str:
    """Appelle un outil sur le serveur MCP. Usage : appeler_outil_mcp("get_time")"""
    return asyncio.run(_appeler_outil(nom_outil, kwargs))

messages = [
    {"role": "system", "content": """\
Tu es un assistant CRM. Pour CHAQUE message, réponds UNIQUEMENT en JSON valide.
Si l'utilisateur veut l'heure              : {"action": "GET_TIME"}
Si l'utilisateur parle d'un client         : {"action": "SEARCH_CLIENT", "nom": "prénom nom exact"}
Pour toute autre réponse                   : {"action": "RESPOND", "message": "ta réponse"}"""}
]

print("=== Agent MCP Démarré ===")

while True:
    user_input = input("\nVous: ")
    if user_input.lower() in ['quit', 'exit']:
        break

    messages.append({"role": "user", "content": user_input})
    payload = {"model": MODEL, "messages": messages, "stream": False, "format": "json"}
    
    try:
        raw = requests.post(OLLAMA_URL, json=payload).json()["message"]["content"]
    except Exception as e:
        print(f"[⚠️ ERREUR API] {e}")
        continue
        
    messages.append({"role": "assistant", "content": raw})

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[⚠️ ERREUR JSON] {raw}")
        continue

    action = data.get("action", "RESPOND")

    if action == "GET_TIME":
        # 🎯 COMPLÉTÉ (9) : Appel de l'outil sans argument
        resultat = appeler_outil_mcp("get_time")
        print(f"  [MCP] get_time → {resultat}")
        
        messages.append({"role": "user", "content": f"[SYSTÈME - MCP] Heure : {resultat}. Formule ta réponse."})
        response2 = requests.post(OLLAMA_URL, json={"model": MODEL, "messages": messages, "stream": False, "format": "json"}).json()
        final = json.loads(response2["message"]["content"])
        messages.append({"role": "assistant", "content": response2["message"]["content"]})
        print(f"\nAgent: {final.get('message', final)}")

    elif action == "SEARCH_CLIENT":
        nom = data.get("nom", "")
        # 🎯 COMPLÉTÉ (10) : Appel de l'outil en passant le kwarg "nom"
        resultat = appeler_outil_mcp("search_client", nom=nom)
        print(f"  [MCP] search_client({nom}) → {resultat}")
        
        messages.append({"role": "user", "content": f"[SYSTÈME - MCP] {resultat}. Formule ta réponse."})
        response2 = requests.post(OLLAMA_URL, json={"model": MODEL, "messages": messages, "stream": False, "format": "json"}).json()
        final = json.loads(response2["message"]["content"])
        messages.append({"role": "assistant", "content": response2["message"]["content"]})
        print(f"\nAgent: {final.get('message', final)}")

    elif action == "RESPOND":
        print(f"\nAgent: {data.get('message', '')}")
