import streamlit as st
import pandas as pd
import altair as alt
from pymongo import MongoClient

st.sidebar.header("🔄 Recargar datos")

if st.sidebar.button("Actualizar datos ahora"):
    st.rerun()

# 🔌 Conexión a MongoDB
client = MongoClient("mongodb://root:example@mongo:27017/")
db_processed = client["etl_processed"]
db_summary = client["etl_summary"]

st.set_page_config(page_title="Global Financial Dashboard", layout="wide")
st.title("📊 Global Financial Dashboard")

# ---------------------------- FIAT RATES ----------------------------
st.subheader("💱 Tasas de Cambio (Fiat)")

forex_data = list(db_processed.forex_history.find())
if forex_data:
    df_fiat = pd.DataFrame(forex_data)
    df_fiat["date"] = pd.to_datetime(df_fiat["date"])
    currencies = df_fiat["target"].unique().tolist()
    selected = st.multiselect("Selecciona monedas:", currencies, default=currencies[:3])

    if selected:
        chart = (
            alt.Chart(df_fiat[df_fiat["target"].isin(selected)])
            .mark_line(point=True)
            .encode(
                x="date:T",
                y="rate:Q",
                color="target:N",
                tooltip=["base", "target", "rate", "change_pct", "date"]
            )
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)
else:
    st.warning("No hay datos históricos de tipo de cambio.")

# ---------------------------- CRYPTO ----------------------------
st.subheader("₿ Criptomonedas")

crypto_data = list(db_processed.crypto_rates.find())
if crypto_data:
    df_crypto = pd.DataFrame(crypto_data)
    df_crypto["date"] = pd.to_datetime(df_crypto["date"])
    df_crypto = df_crypto[df_crypto["currency"] == "usd"]

    chart = (
        alt.Chart(df_crypto)
        .mark_line(point=True)
        .encode(
            x="date:T",
            y="rate:Q",
            color="crypto:N",
            tooltip=["crypto", "rate", "date"]
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("No hay datos de criptomonedas.")

# ---------------------------- PIB ----------------------------
st.subheader("📈 PIB histórico de México (USD)")

gdp_data = list(db_processed.worldbank_gdp.find())
if gdp_data:
    df_gdp = pd.DataFrame(gdp_data)
    df_gdp["gdp_billion"] = df_gdp["gdp"] / 1e9
    df_gdp["date"] = pd.to_datetime(df_gdp["date"])
    df_gdp = df_gdp.sort_values("date")

    chart = (
        alt.Chart(df_gdp)
        .mark_area(opacity=0.5)
        .encode(
            x="date:T",
            y=alt.Y("gdp_billion:Q", title="PIB (Billones USD)"),
            tooltip=["date", "gdp_billion"]
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("No hay datos de PIB.")

# ---------------------------- GEMINI SUMMARY ----------------------------
st.subheader("🧠 Resumen automático (Gemini AI)")

summary_doc = db_summary.gemini_summary.find_one(sort=[("date", -1)])
if summary_doc:
    st.markdown(f"📅 Fecha del resumen: `{summary_doc['date']}`")
    st.markdown(summary_doc["summary"])
else:
    st.info("No se encontró ningún resumen generado por Gemini.")