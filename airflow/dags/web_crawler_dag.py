from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators import PythonOperator
from crawler.crawler import WebCrawler

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
    'web_crawler',
    default_args=default_args,
    description='A DAG to run web crawler',
    schedule_interval=timedelta(days=1),
)

def run_crawler(**kwargs):
    base_url = kwargs['dag_run'].conf.get('base_url', 'https://www.24h.com.vn/')
    crawler = WebCrawler(base_url)
    crawler.crawl()
    crawler.close()

crawl_task = PythonOperator(
    task_id='crawl_website',
    python_callable=run_crawler,
    provide_context=True,
    dag=dag,
)

crawl_task