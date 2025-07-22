from pymongo import MongoClient
from datetime import datetime
from airflow.models import Variable

def load_all(ti):
    mongo_uri = Variable.get("mongo_uri", default_var="mongodb://root:example@mongo:27017/admin")
    client = MongoClient(mongo_uri)
    
    db_raw = client["etl_raw"]
    db_processed = client["etl_processed"]

    # 1. Extraídos (datos crudos)
    latest_data = ti.xcom_pull(task_ids="extract_latest", key="latest_rates")
    if latest_data:
        db_raw["forex_latest_raw"].insert_one(latest_data)
        print("✅ forex_latest_raw cargado")

    historical_data = ti.xcom_pull(task_ids="extract_historical", key="historical_rates")
    if historical_data:
        db_raw["forex_history_raw"].insert_one(historical_data)
        print("✅ forex_history_raw cargado")

    crypto_data = ti.xcom_pull(task_ids="extract_crypto", key="crypto_rates")
    if crypto_data:
        db_raw["crypto_rates_raw"].insert_one({"timestamp": datetime.now(), "data": crypto_data})
        print("✅ crypto_rates_raw cargado")

    gdp_data = ti.xcom_pull(task_ids="extract_gdp", key="gdp_data")
    if gdp_data:
        db_raw["worldbank_gdp_raw"].insert_one({"timestamp": datetime.now(), "data": gdp_data})
        print("✅ worldbank_gdp_raw cargado")

#------------------------------ 2. Transformados (datos limpios)-------------------------------------------#
    transformed_latest = ti.xcom_pull(task_ids="transform_all", key="transformed_latest")
    if transformed_latest:
        db_processed["forex_latest"].insert_many(transformed_latest)

    transformed_history = ti.xcom_pull(task_ids="transform_all", key="transformed_historical")
    if transformed_history:
        db_processed["forex_history"].insert_many(transformed_history)

    transformed_crypto = ti.xcom_pull(task_ids="transform_all", key="transformed_crypto")
    if transformed_crypto:
        db_processed["crypto_rates"].insert_many(transformed_crypto)

    transformed_gdp = ti.xcom_pull(task_ids="transform_all", key="transformed_gdp")
    if transformed_gdp:
        db_processed["worldbank_gdp"].insert_many(transformed_gdp)
