# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime, timedelta
# from utils.utils import apply_services

# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'start_date': datetime(2024, 1, 1),
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'apply_services',
#     default_args=default_args,
#     description='Scrape tweets and save to PostgreSQL and CSV',
#     schedule_interval=timedelta(days=1),
# )

# scrape_task = PythonOperator(
#     task_id='apply_services',
#     python_callable=apply_services,
#     dag=dag,
# )

# scrape_task 
