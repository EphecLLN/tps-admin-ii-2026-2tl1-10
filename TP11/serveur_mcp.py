# serveur_mcp.py
import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OutilsAdmin")

@mcp.tool()
def get_time() -> str:
    """Retourne l'heure système au format HH:MM:SS."""
    return datetime.datetime.now().strftime("%H:%M:%S")

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
    mcp.run(transport='stdio')
