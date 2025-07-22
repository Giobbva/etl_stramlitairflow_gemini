import requests
from airflow.models import Variable
from datetime import datetime

URL = "https://api.frankfurter.dev"

# ---------------------------------------------------------------------------------------------------- #
def extract_latest_rates(ti):
    symbols = Variable.get("currencies", default_var="USD,EUR,JPY")
    base = Variable.get("base_currency", default_var="MXN")
    url = f"{URL}/v1/latest?base={base}&symbols={symbols}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        ti.xcom_push(key="latest_rates", value=response.json())
        print("✅ Datos en streaming extraídos (Frankfurter)")
    except Exception as e:
        print(f"❌ Error Frankfurter latest: {e}")
        ti.xcom_push(key="latest_rates", value=None)

# ---------------------------------------------------------------------------------------------------- #

def extract_historical_rates(ti):
    base = Variable.get("base_currency", default_var="EUR")
    symbols = Variable.get("currencies", default_var="USD,MXN,JPY")
    xcom_start = ti.xcom_pull(task_ids="start", key="history_start")
    xcom_end = ti.xcom_pull(task_ids="start", key="history_end")
    start_date = xcom_start or Variable.get("history_start", default_var="2024-01-01")
    end_date = xcom_end or Variable.get("history_end", default_var=datetime.now().strftime("%Y-%m-%d"))

    url = f"{URL}/v1/{start_date}..{end_date}?base={base}&symbols={symbols}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        ti.xcom_push(key='historical_rates', value=response.json())
        print(f"✅ Datos históricos extraídos: {start_date} → {end_date}")
    except Exception as e:
        print(f"❌ Error Frankfurter históricos: {e}")
        ti.xcom_push(key='historical_rates', value=None)

# ---------------------------------------------------------------------------------------------------- #

def extract_crypto_rates(ti):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,eur,mxn"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        ti.xcom_push(key='crypto_rates', value=response.json())
        print("✅ Tasas de criptomonedas extraídas (CoinGecko)")
    except Exception as e:
        print(f"❌ Error al extraer datos de CoinGecko: {e}")
        ti.xcom_push(key='crypto_rates', value=None)

# ---------------------------------------------------------------------------------------------------- #

def extract_worldbank_gdp(ti):
    url = "http://api.worldbank.org/v2/country/mx/indicator/NY.GDP.MKTP.CD?format=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        ti.xcom_push(key="gdp_data", value=data)
        print("✅ PIB extraído de World Bank")
    except Exception as e:
        print(f"❌ Error al obtener PIB de World Bank: {e}")
        ti.xcom_push(key="gdp_data", value=None)