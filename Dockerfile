# 1. Point de départ — quelle image de base utiliser ?
FROM python:3.12-slim
# "slim" = version légère de Python, sans outils inutiles
# Règle : toujours préciser la version exacte en production

# 2. Dossier de travail dans le conteneur
WORKDIR /app
# Tous les fichiers copiés iront dans /app
# Comme faire "cd /app" dans le conteneur

# 3. Copier d'abord les dépendances
COPY requirements.txt .
# On copie SEULEMENT requirements.txt en premier
# Pourquoi ? Pour profiter du cache Docker (optimisation)

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt
# --no-cache-dir = ne pas garder le cache pip dans l'image
# → image plus légère

# 5. Copier le reste du code
COPY . .
# Copie tout le projet dans /app

# 6. Exposer le port
EXPOSE 8000
# Dit à Docker "ce conteneur écoute sur le port 8000"
# Note : c'est informatif, pas suffisant seul

# 7. Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# --host 0.0.0.0 = écouter sur toutes les interfaces réseau
# IMPORTANT : sans ça, ton app n'est pas accessible depuis l'extérieur