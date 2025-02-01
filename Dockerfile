# Dockerfile simplifié pour Airflow
FROM apache/airflow:2.7.1-python3.10

# Copier le fichier requirements
COPY --chown=airflow:root requirements /requirements

# Créer les répertoires nécessaires s'ils n'existent pas et définir les permissions
USER root
RUN mkdir -p /opt/airflow/dags /opt/airflow/plugins /opt/airflow/logs /opt/airflow/data && \
    chown -R airflow:root /opt/airflow/dags /opt/airflow/plugins /opt/airflow/logs /opt/airflow/data && \
    chmod -R 755 /opt/airflow/dags /opt/airflow/plugins /opt/airflow/logs /opt/airflow/data

# Copier les DAGs et plugins dans les dossiers appropriés
COPY --chown=airflow:root ./airflow/dags /opt/airflow/dags
COPY --chown=airflow:root ./airflow/plugins /opt/airflow/plugins

# Passer à l'utilisateur Airflow pour les installations pip
USER airflow

# Installer les dépendances nécessaires depuis le fichier requirements
RUN pip install -r /requirements/local

# Installer twikit
RUN pip install twikit

# Installer NLTK et télécharger les modules nécessaires
RUN pip install nltk && \
    python -c "import nltk; nltk.download(['stopwords', 'punkt', 'wordnet', 'omw-1.4', 'punkt_tab'])"


# # Dockerfile simplifié pour Airflow
# FROM apache/airflow:2.7.1-python3.10

# # Copier le fichier requirements
# COPY --chown=airflow:root requirements /requirements

# # Créer les répertoires nécessaires s'ils n'existent pas et définir les permissions
# USER root
# RUN mkdir -p /opt/airflow/dags /opt/airflow/plugins /opt/airflow/logs /opt/airflow/data && \
#     chown -R airflow:root /opt/airflow/dags /opt/airflow/plugins /opt/airflow/logs /opt/airflow/data && \
#     chmod -R 755 /opt/airflow/dags /opt/airflow/plugins /opt/airflow/logs /opt/airflow/data

# # Copier les DAGs et plugins dans les dossiers appropriés
# COPY --chown=airflow:root ./airflow/dags /opt/airflow/dags
# COPY --chown=airflow:root ./airflow/plugins /opt/airflow/plugins

# # Passer à l'utilisateur Airflow pour les installations pip
# USER airflow

# # Installer les dépendances nécessaires depuis le fichier requirements
# RUN pip install -r /requirements/local

# # Installer twikit
# RUN pip install twikit
