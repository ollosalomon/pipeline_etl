# créer un dag airflow avec l'operateur pythonoperator

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from utils.utils import my_python_function

    
with DAG(
    dag_id="test_dag",
    start_date=datetime(2024,10,20)
) as dag:
    python_task = PythonOperator(
        task_id="run_my_python_function",
        python_callable=my_python_function
    )