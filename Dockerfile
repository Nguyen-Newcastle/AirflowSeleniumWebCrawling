#FROM apache/airflow:2.4.1-python3.9

#USER airflow

#COPY ./dags /opt/airflow/dags
# Copy your custom DAGs and plugins to the appropriate directories
#COPY ./logs /opt/airflow/logs
#COPY ./plugins /opt/airflow/plugins

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install any needed packages specified in requirements.txt
COPY airflow/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install "apache-airflow==2.4.2" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.4.2/constraints-3.10.txt"