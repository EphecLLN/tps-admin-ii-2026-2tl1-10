# 1. On part d'une image Pyton légère (slim)
FROM python:3.9-slim

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. Copie du script du PC hôte vers le conteneur
COPY date.py . 

# 4. La commande qui se lance au démarrage
# A la fin de cette commande, le contenur s'éteint
CMD ["python", "date.py"]