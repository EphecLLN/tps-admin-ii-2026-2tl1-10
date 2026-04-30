import datetime
from mcp.server.fastmcp import FastMCP

# 🎯 LA CORRECTION EST ICI : 
# On donne l'adresse (0.0.0.0) et le port (8000) dès la création de l'objet
mcp = FastMCP("OutilsAdmin", host="0.0.0.0", port=8000)

@mcp.tool()
def ephec_time() -> str:
    """Retourne l'heure selon le format propriétaire EPHEC : préfixe EPHEC suivi de l'heure inversée (SS:MM:HH)."""
    heure = datetime.datetime.now().strftime("%H:%M:%S")
    return f"EPHEC | {heure[::-1]}"

@mcp.tool()
def search_client(nom: str) -> str:
    """Recherche un client dans clients.csv par son nom."""
    try:
        with open("clients.csv", "r") as f:
            for ligne in f:
                if nom.lower() in ligne.lower():
                    return ligne.strip()
    except FileNotFoundError:
        return "Erreur : clients.csv introuvable."
    return "Non trouvé."

if __name__ == "__main__":
    # 🎯 LA CORRECTION EST ICI :
    # On lance le serveur avec le transport "sse" (la brique HTTP derrière MCP)
    mcp.run(transport='sse')
