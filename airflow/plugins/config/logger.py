import logging
import os

class Logger:
    def __init__(self, name, level):
        # Créer le nom du fichier de log
        name = name + ".log"
        
        # Chemin du répertoire de logs
        log_dir = os.path.join("/opt/airflow/logs", "logs")
        os.makedirs(log_dir, exist_ok=True)  # Créer le répertoire s'il n'existe pas
        
        file_path = os.path.join(log_dir, name)

        # Configuration du logger
        logger = logging.getLogger(name)
        logger.propagate = False
        logger.setLevel(level)

        if not logger.hasHandlers():
            formatter = logging.Formatter(
                "%(asctime)s: %(name)s: [%(levelname)s]: %(message)s"
            )
            fh = logging.FileHandler(file_path)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        self.logger = logger


# import logging
# import os


# # Defining loggers


# class Logger:
#     def __init__(self, name, level):
#         name = name + ".log"
#         os.makedirs(os.path.join("/", "app/airflow/logs", "logs"), exist_ok=True)

#         file_path = os.path.join("/", "app/airflow/logs", "logs", name)

#         logger = logging.getLogger(name)
#         logger.propagate = False
#         logger.setLevel(level)

#         if not logger.hasHandlers():
#             formatter = logging.Formatter(
#                 "%(asctime)s: %(name)s: [%(levelname)s]: %(message)s"
#             )
#             fh = logging.FileHandler(file_path)
#             fh.setLevel(level)
#             fh.setFormatter(formatter)
#             logger.addHandler(fh)

#         self.logger = logger
