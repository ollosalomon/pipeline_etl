from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from scrape_test.scraper import scrape_tweets, save_tweets_to_db , preprocessing_data, apply_services, insert_tweets_to_db_after_apply_service

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'twitter_scraper',
    default_args=default_args,
    description='Scrape tweets and save to PostgreSQL and CSV',
    schedule_interval=timedelta(days=1),
)

_scrape_task = PythonOperator(
    task_id='scrape_tweets',
    python_callable=scrape_tweets,
    dag=dag,
)

_preprocess_task = PythonOperator(
    task_id='processing_tweets',
    python_callable=preprocessing_data,
    dag=dag,
)

_save_to_db_task = PythonOperator(
    task_id='save_tweets_to_db',
    python_callable=save_tweets_to_db,
    dag=dag,
)


dag = DAG(
    'apply_service',
    default_args=default_args,
    description='apply_service and save to PostgreSQL',
    schedule_interval=timedelta(days=1),
)


_apply_services = PythonOperator(
    task_id='apply_services',
    python_callable=apply_services,
    dag=dag,
)

_save_to_db_task = PythonOperator(
    task_id='save_to_db_task',
    python_callable=insert_tweets_to_db_after_apply_service,
    dag=dag,
)

_scrape_task >> _preprocess_task >> _save_to_db_task

_apply_services >> _save_to_db_task
