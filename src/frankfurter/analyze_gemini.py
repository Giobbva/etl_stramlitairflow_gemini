import requests
from airflow.models import Variable
from pymongo import MongoClient
from datetime import datetime

def analyze_with_gemini():
    # Conectar a MongoDB
    mongo_uri = Variable.get("mongo_uri", default_var="mongodb://root:example@mongo:27017/admin")
    client = MongoClient(mongo_uri)
    db = client["etl_processed"]

    prompt_lines = [
        "Analiza la siguiente información financiera de tipo de cambio, criptomonedas y PIB para generar un resumen comparativo e identificar tendencias y anomalías:\n"
    ]

    # FOREX LATEST
    latest = list(db["forex_latest"].find().sort("date", -1).limit(5))
    for item in latest:
        line = f"[FOREX] {item['base']} → {item['target']}: {item['rate']} ({item.get('change_pct', 'N/A')}% cambio)"
        prompt_lines.append(line)

    # FOREX HISTÓRICO
    historical = list(db["forex_history"].find().sort("date", -1).limit(5))
    for item in historical:
        line = f"[HISTORICAL] {item['base']} → {item['target']}: {item['rate']} ({item.get('change_pct', 'N/A')}% cambio)"
        prompt_lines.append(line)

    # CRYPTO
    crypto = list(db["crypto_rates"].find().sort("date", -1).limit(5))
    for item in crypto:
        line = f"[CRYPTO] {item['crypto']} → {item['currency']}: {item['rate']} ({item['date']})"
        prompt_lines.append(line)

    # GDP
    gdp = list(db["worldbank_gdp"].find().sort("date", -1).limit(5))
    for item in gdp:
        line = f"[GDP] {item['country']}: {item['gdp']} USD en {item['date']}"
        prompt_lines.append(line)

    prompt_text = "\n".join(prompt_lines)

    # Obtener API key de Gemini desde Variable
    api_key = Variable.get("gemini_api_key", default_var=None)
    if not api_key:
        print("❌ Falta la Variable 'gemini_api_key'")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = { "Content-Type": "application/json" }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()

        summary = result["candidates"][0]["content"]["parts"][0]["text"]
        print("✅ Resumen generado por Gemini:\n", summary)

        # Guardar resumen en nueva colección
        summary_db = client["etl_summary"]
        summary_db["gemini_summary"].insert_one({
            "source": "gemini",
            "summary": summary,
            "date": datetime.now()
        })
        print("✅ Resumen almacenado en etl_summary.gemini_summary")

    except Exception as e:
        print(f"❌ Error al procesar Gemini: {e}")
