<<<<<<< HEAD
# 🚀 ETL Financial Pipeline with Airflow + MongoDB + Gemini + Streamlit

This project runs a complete ETL pipeline that extracts financial and economic data from public APIs, processes it with Airflow, stores it in MongoDB, analyzes it using Google's Gemini API, and visualizes the results with Streamlit.

-------------------------------------------------------------------------------

📁 Project Structure
```
project/
├── app/
│   ├── Dockerfile               # Streamlit image
│   ├── pages/
│   │   └── dashboard.py         # Streamlit dashboard
│   └── requirements.txt
├── dags/
│   └── main_pipeline.py         # Main Airflow DAG
├── src/
│   └── frankfurter/
│       ├── analyze_gemini.py
│       ├── extract.py
│       ├── load.py
│       ├── transform.py
│       └── __init__.py
├── docker-compose.yml
├── Dockerfile                   # Airflow image
├── requirements.txt
└── README.md
```
-------------------------------------------------------------------------------

⚙️ Requirements

- Docker and Docker Compose installed
- Gemini API key (optional if not using Gemini analysis)

-------------------------------------------------------------------------------

🚀 How to Initialize the Project

1. Clone the repository

    git clone https://github.com/youruser/etl-finance-project.git
    
    cd etl-finance-project/project

2. Initialize Airflow's database

    docker compose up init

    📝 This command initializes Airflow's metadata DB. Run it before anything else.

3. Build and start all containers

    docker compose up --build

    ✅ Wait a few minutes until all services (Airflow, MongoDB, Streamlit) are ready.

4. Create an Airflow user (only once)

    docker compose exec webserver airflow users create \
      --username airflow \
      --password airflow \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com

5. To restart de creation of the docker
    
    docker compose down --volumes --remove-orphans

-------------------------------------------------------------------------------

🌐 Web Interfaces

Service        | URL                    | User / Password
---------------|------------------------|---------------------
Airflow UI     | http://localhost:8080  | airflow / airflow
Streamlit App  | http://localhost:8501  | —
MongoDB Shell  | via Docker             | root / example

-------------------------------------------------------------------------------

🔁 ETL Pipeline Flow

Stage      | Description                                                   | MongoDB DB / Collection
-----------|---------------------------------------------------------------|-----------------------------
Extract    | Pulls data from APIs (Frankfurter, CoinGecko, World Bank)     | — (data held in memory)
Load       | Saves raw data into `etl_raw.*` collections                   | `etl_raw`
Transform  | Reads from `etl_raw`, processes data into `etl_processed.*`   | `etl_processed`
Gemini     | Reads from `etl_processed`, generates summary                 | `etl_summary.summary`
Dashboard  | Reads from `etl_processed` and `etl_summary` for display      | Both

-------------------------------------------------------------------------------

🔐 Set Gemini API Key (if needed)

    docker compose exec webserver airflow variables set gemini_api_key YOUR_API_KEY

-------------------------------------------------------------------------------

🧪 Useful Commands

- View Airflow logs:

    docker compose logs webserver

- Enter MongoDB shell:

    docker exec -it mongodb mongosh -u root -p example --authenticationDatabase admin

- Explore MongoDB databases:

    show dbs
    use etl_processed
    show collections
    db.crypto_rates.findOne()

-------------------------------------------------------------------------------

✅ Project Status

- ✅ DAG working end-to-end
- ✅ Raw and processed data separated in MongoDB
- ✅ Gemini summary created and stored
- ✅ Streamlit dashboard displays data

-------------------------------------------------------------------------------

📝 Notes

This architecture supports real-time or batch extensions and is ideal for data engineering practice, academic use, or rapid prototyping of data pipelines.
=======
# etl_stramlitairflow_gemini
Giovanni Rafael Soriano Pacheco project where I used dags with airflow and it is charged to streamlit by mongo
>>>>>>> 7fd6d6be8c97dc74eba2851806e9e1e8cb84584b
