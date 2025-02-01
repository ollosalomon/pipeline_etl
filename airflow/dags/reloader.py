import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DAGFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_reload_time = time.time()
        self.cooldown_period = 5  # Secondes entre les rechargements

    def on_any_event(self, event):
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.py'):
            return

        current_time = time.time()
        if current_time - self.last_reload_time < self.cooldown_period:
            return

        logger.info(f"Detected change in {event.src_path}")
        self.trigger_dag_reload()
        self.last_reload_time = current_time

    def trigger_dag_reload(self):
        try:
            response = requests.get(
                "http://airflow-webserver:8080/api/v1/dags",
                auth=("admin", "admin"),
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                logger.info("Successfully triggered DAG reload")
            else:
                logger.error(f"Failed to trigger reload: {response.status_code}")
        except Exception as e:
            logger.error(f"Error triggering reload: {str(e)}")

if __name__ == "__main__":
    path = "/opt/airflow/dags"
    event_handler = DAGFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logger.info(f"Started watching directory: {path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopping DAG file observer")
    observer.join()