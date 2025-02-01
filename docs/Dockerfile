# Dockerfile simplifié pour le service docs
FROM python:3.10-slim

# Installer les dépendances nécessaires pour mkdocs
COPY requirements /requirements
RUN pip install --no-cache-dir -r /requirements/docs

# Définir le dossier de travail et copier le code
WORKDIR /app
COPY . /app

# Changer le répertoire de travail pour aller là où se trouve mkdocs.yml
WORKDIR /app/docs

# Exécuter le service de documentation
CMD ["mkdocs", "serve", "-a", "0.0.0.0:9000"]
