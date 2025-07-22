import requests
from airflow.models import Variable
from pymongo import MongoClient
from datetime import datetime

def analyze_with_gemini():
    # Conectar a MongoDB
    mongo_uri = Variable.get("mongo_uri", default_var="mongodb://root:example@mongo:27017/admin")
    client = MongoClient(mongo_uri)
    db = client["etl_processed"]
    
    # Leer últimos documentos de 'forex_latest'
    latest_data = list(db["forex_latest"].find().sort("date", -1).limit(10))

    if not latest_data:
        print("❌ No se encontró información en 'forex_latest'")
        return

    # Crear prompt para Gemini
    prompt_lines = [
        "Analiza los siguientes cambios de tipo de cambio entre monedas y genera un resumen claro, "
        "indicando las monedas más volátiles y cualquier tendencia observada:\n"
    ]
    for item in latest_data:
        line = f"{item['base']} → {item['target']}: {item['rate']} ({item.get('change_pct', 'N/A')}% cambio)"
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