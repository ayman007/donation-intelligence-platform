# Architecture

```mermaid
flowchart LR
  SIM["Event simulator"] --> KAFKA["Kafka + Schema Registry"]
  KAFKA --> RAW[("Snowflake RAW")]
  BATCH["Batch files"] --> S3[("S3 landing, eu-north-1")]
  S3 --> RAW
  RAW --> DBT["dbt: staging, intermediate, marts"]
  DBT --> MARTS[("Snowflake MARTS")]
  MARTS --> RAG["LLM / RAG layer"]
  MARTS --> APP["Streamlit app"]
  RAG --> APP
  AIRFLOW["Airflow"] -.->|orchestrates| S3
  AIRFLOW -.->|orchestrates| DBT
  AIRFLOW -.->|orchestrates| RAG
  TF["Terraform"] -.->|provisions| S3
  TF -.->|provisions| RAW
```

## Components
| Layer | Tool | Role |
|---|---|---|
| Infrastructure | Terraform | AWS and Snowflake resources as code |
| Streaming | Kafka | Real-time app events |
| Warehouse | Snowflake | RAW, STAGING, MARTS |
| Transformation | dbt | Models, tests, docs |
| Orchestration | Airflow | Batch loads, dbt runs, quality checks |
| AI | LLM / RAG | Text-to-SQL and retrieval over marts and docs |
