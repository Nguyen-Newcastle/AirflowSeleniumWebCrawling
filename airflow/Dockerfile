FROM apache/airflow:2.4.1-python3.9

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --user -r /requirements.txt

COPY ./dags /opt/airflow/dags
# Copy your custom DAGs and plugins to the appropriate directories
COPY ./logs /opt/airflow/logs
COPY ./plugins /opt/airflow/plugins