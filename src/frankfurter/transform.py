from datetime import datetime

def transform_latest(ti):
    latest_data = ti.xcom_pull(task_ids="extract_latest", key="latest_rates")
    if not latest_data:
        print("No se encontró latest_rates en Xcom.")
        ti.xcom_push(key="transformed_latest", value=None)
        return
    
    #========================|
    # ASIGNAMOS LAS VARIABLES|
    #========================|
    base = latest_data["base"]
    date = latest_data["date"]
    rates = latest_data["rates"]

    previous_rates = ti.xcom_pull(task_ids="load_latest", key="latest_rates_backup") or {}

    transformed = []
    for currency, rate in rates.items():
        previous = previous_rates.get(currency)
        change = rate - previous if previous else None
        change_pct = ((change / previous) * 100) if previous else None

        transformed.append({
            "base": base,
            "target": currency,
            "date": date,
            "rate": rate,
            "previous_rate": previous,
            "change": round(change, 6) if change is not None else None,
            "change_pct": round(change_pct, 4) if change_pct is not None else None
        })

    print("✅ Datos transformados (últimos):", transformed[:2], "...")
    return transformed


#------------------------------------------------------------------------------------------------------#

def transform_historical(ti):
    historical_data = ti.xcom_pull(task_ids="extract_historical", key="historical_rates")
    if not historical_data:
        print("No se encontró 'historical_rates' en XCom.")
        ti.xcom_push(key="transformed_historical", value=None)
        return

    base = historical_data["base"]
    rates_by_day = historical_data["rates"]

    transformed = []
    sorted_dates = sorted(rates_by_day.keys())
    previous_day = None

    for date in sorted_dates:
        daily_rates = rates_by_day[date]
        for currency, rate in daily_rates.items():
            # Calcular variación con respecto al día anterior
            prev_rate = rates_by_day[previous_day][currency] if previous_day else None
            change = rate - prev_rate if prev_rate else None
            change_pct = ((change / prev_rate) * 100) if prev_rate else None

            transformed.append({
                "base": base,
                "target": currency,
                "date": date,
                "rate": rate,
                "previous_rate": prev_rate,
                "change": round(change, 6) if change else None,
                "change_pct": round(change_pct, 4) if change_pct else None
            })

        previous_day = date

    print("Datos transformados (históricos):", transformed[:3], "...")
    return transformed


#---------------------------------------------------------------------------------------------------------------------#

def transform_crypto(ti):
    crypto_data = ti.xcom_pull(task_ids="extract_crypto", key="crypto_rates")
    if not crypto_data:
        print("❌ No se encontró 'crypto_rates' en XCom.")
        ti.xcom_push(key="transformed_crypto", value=None)
        return

    transformed = []
    date = datetime.now().strftime("%Y-%m-%d")

    for coin, values in crypto_data.items():
        for currency, rate in values.items():
            transformed.append({
                "crypto": coin,
                "currency": currency,
                "rate": rate,
                "date": date
            })

    print("✅ Datos transformados (cripto):", transformed)
    return transformed

#---------------------------------------------------------------------------------------------------------------------#

def transform_gdp(ti):
    gdp_data = ti.xcom_pull(task_ids="extract_gdp", key="gdp_data")
    if not gdp_data or len(gdp_data) < 2:
        print("❌ No se encontró 'gdp_data' válido en XCom.")
        ti.xcom_push(key="transformed_gdp", value=None)
        return

    observations = gdp_data[1]
    transformed = []

    for entry in observations:
        transformed.append({
            "country": entry.get("country", {}).get("value", "Unknown"),
            "date": entry.get("date"),
            "gdp": entry.get("value")
        })

    print("✅ Datos transformados (PIB):", transformed[:3])   
    return transformed

def transform_all(ti):
    latest_data = transform_latest(ti)
    ti.xcom_push(key="transformed_latest", value=latest_data)

    historical_data = transform_historical(ti)
    ti.xcom_push(key="transformed_historical", value=historical_data)

    crypto_data = transform_crypto(ti)
    ti.xcom_push(key="transformed_crypto", value=crypto_data)

    gdp_data = transform_gdp(ti)
    ti.xcom_push(key="transformed_gdp", value=gdp_data)