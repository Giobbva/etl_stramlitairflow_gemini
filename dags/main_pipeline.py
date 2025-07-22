from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import sys

# Inserta la ruta real al proyecto (sube un nivel desde /opt/airflow/dags)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Set Airflow variable from env var (if not already set)
if not Variable.get("gemini_api_key", default_var=None):
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        Variable.set("gemini_api_key", api_key)

# Funciones ETL
from frankfurter.extract import (
    extract_latest_rates,
    extract_historical_rates,
    extract_crypto_rates,
    extract_worldbank_gdp,
)
from frankfurter.transform import transform_all

from frankfurter.load import load_all

from frankfurter.analyze_gemini import analyze_with_gemini

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 7, 21),
}

with DAG(
    dag_id="main_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "forex", "crypto", "gdp"],
) as dag:

    # --- Frankfurter ---
    extract_latest = PythonOperator(
        task_id="extract_latest", python_callable=extract_latest_rates
    )

    extract_historical = PythonOperator(
        task_id="extract_historical", python_callable=extract_historical_rates
    )

    # --- Crypto (CoinGecko) ---
    extract_crypto = PythonOperator(
        task_id="extract_crypto", python_callable=extract_crypto_rates
    )


    # --- GDP (World Bank) ---
    extract_gdp = PythonOperator(
        task_id="extract_gdp", python_callable=extract_worldbank_gdp
    )

    transform_task = PythonOperator(
        task_id="transform_all",
        python_callable=transform_all
    )

    load_task = PythonOperator(
        task_id="load_all",
        python_callable=load_all
    )

    # --- Analyze with Gemini ---
    analyze_task = PythonOperator(
        task_id="analyze_with_gemini", python_callable=analyze_with_gemini
    )

    # --- Dependencias ---
    [extract_latest, extract_historical, extract_crypto, extract_gdp] >> transform_task >> load_task >> analyze_task

