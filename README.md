## 🌦️ Real-Time Weather Data Pipeline with AWS

This project demonstrates a real-time ETL pipeline using AWS services.
It fetches weather data from a public API, ingests it into AWS, processes it, and makes it queryable with Athena.

## 🚀 Architecture Overview

## Pipeline flow:

Producer fetches weather data from WeatherAPI (via REST API).

Lambda ETL transforms & stores JSON into S3 (raw folder).

AWS Glue Crawler scans raw JSON → creates schema in Data Catalog.

Amazon Athena queries structured weather data.

Step Functions orchestrate the end-to-end flow.

CloudWatch & SNS provide monitoring and alerts.


## 📂 Project Structure
Weather_API_Real_Time_Project/
│── docs/                           # Documentation + diagrams + screenshots
│   └── readme_images/              # Screenshots used in README (Athena, S3, Step Functions, etc.)
│
│── glue/                           # AWS Glue configurations
│   └── crawler_config.md           # Notes on Glue crawler setup (weather-data-crawler)
│
│── lambda/                         # Lambda functions (ETL & processing logic)
│   └── etl-weather-transform/
│       ├── lambda_transform.py     # Lambda code for parsing & cleaning weather data
│       └── lambda_transform_After...py # Alternate version after removing Kinesis
│
│── producer/                       # Data ingestion scripts
│   └── weather_api_producer.py     # Python script to fetch Weather API data and push to Kinesis/S3
│
│── step_functions/                 # Workflow orchestration
│   └── weather_pipeline_workflow.asl.json  # Step Functions definition (Lambda → Glue → Athena → Success)
│
│── .env                            # Environment variables (API key, bucket name, region, etc.)
│── .gitignore                      # Prevents committing secrets like `.env` and unnecessary files
│── requirements.txt                # Python dependencies for producer & local testing
│── README.md                       # Main project documentation (overview, steps, diagrams, usage)

## 📑 Why Each File/Folders Exists

docs/ → contains diagrams (like architecture.png) and screenshots (Athena queries, CloudWatch, Step Functions flow) for documentation.

glue/crawler_config.md → explains Glue crawler configuration (weather-data-crawler) that scans S3 and updates schema.

lambda/etl-weather-transform/ → holds Lambda transformation code:

Cleans raw JSON from API/Kinesis.

Saves structured data into S3 (raw/ folder).

Alternate version supports direct Step Functions → Lambda → S3 flow.

producer/weather_api_producer.py → script that calls external Weather API and sends data into Kinesis stream (or S3 directly if Kinesis is disabled).

step_functions/weather_pipeline_workflow.asl.json → AWS Step Functions definition for orchestrating the pipeline (Producer → Lambda → Glue → Athena → Success).

.env → sensitive config like API keys, bucket name, region (excluded from GitHub via .gitignore).

.gitignore → makes sure sensitive/unnecessary files like .env, __pycache__/, .DS_Store aren’t pushed to GitHub.

requirements.txt → dependencies (e.g., boto3, requests, python-dotenv) for local testing and running producer script.

README.md → main guide with step-by-step explanation, architecture diagram (Mermaid), and execution details.

## 🔧 End-to-End Technical Workflow
## 1. Weather Data Ingestion

A Python producer script (weather_api_producer.py) calls the [WeatherAPI REST endpoint].

The script retrieves current weather JSON for a specified location.

Instead of storing locally, data is forwarded to the pipeline for processing.

## 2. AWS Lambda – ETL Transformation

Lambda function (lambda_transform.py) receives the raw JSON event.

Handles two event sources:

Step Functions direct payloads (JSON passed inline).

Kinesis records (legacy, with base64 decoding).

Transformation performed:

Extracts city, country, temperature_c, humidity, condition.

Adds ISO 8601 timestamp (datetime.now(datetime.UTC) → non-deprecated).

Output written as JSON file → Amazon S3 under prefix raw/.

Example: s3://<bucket>/raw/weather-data-YYYYMMDDHHMMSS.json.

## 3. Amazon S3 – Data Lake Storage

Acts as the central landing zone.

Folder structure:

s3://<bucket>/raw/                # Incoming raw JSON data
s3://<bucket>/athena-results/     # Athena query results


Each Lambda execution creates a new JSON file in /raw/.

## 4. AWS Glue – Schema Discovery

Glue Crawler (weather-data-crawler) is configured to scan s3://<bucket>/raw/.

Automatically infers schema of JSON files.

Populates AWS Glue Data Catalog with a table:

Database: weather_db

Table: weather_data_jsonraw

Schema includes nested JSON fields (location, current, etc.).

## 5. Amazon Athena – Interactive SQL

Athena queries run on top of the Glue Data Catalog.

Example query:

SELECT
  data.location.name        AS city,
  data.location.country     AS country,
  data.current.temp_c       AS temperature_c,
  data.current.humidity     AS humidity,
  data.current.condition.text AS condition,
  data.current.last_updated AS last_updated
FROM weather_db.weather_data_jsonraw
LIMIT 10;


Results automatically stored in s3://<bucket>/athena-results/.

## 6. AWS Step Functions – Orchestration

State machine (weather_pipeline_workflow.asl.json) orchestrates the flow:

FetchWeatherData → Invokes Lambda ETL.

RunGlueCrawler → Ensures schema is refreshed.

RunAthenaQuery → Runs a pre-defined query for validation.

SuccessState → Marks workflow complete.

All steps are executed sequentially.

## 7. Monitoring & Alerts

CloudWatch Logs → Captures Lambda, Step Functions, and Athena logs.

CloudWatch Alarms → Configured for:

Lambda error rate ≥ threshold.

Step Function execution failures.

SNS Notifications → Sends email alerts when pipeline fails.

## 🔑 Key Technical Notes

Designed for real-time ETL but supports batch re-runs via Step Functions.

Initial design used Kinesis → Lambda → S3, but simplified to Lambda → S3 (removing Kinesis dependency).

Fully serverless architecture — no servers to manage.

Can be extended with EventBridge scheduler to run every X minutes.

## 📊 Architecture Diagram (Mermaid)
flowchart TD

    A[Weather API Producer<br>(Python Script)] -->|REST API JSON| B[Lambda ETL<br>etl-weather-transform]

    B -->|Transformed JSON| C[S3 Bucket<br>praneeth-weather-data/raw]

    C --> D[Glue Crawler<br>weather-data-crawler]
    D --> E[Glue Data Catalog<br>weather_db.weather_data_jsonraw]

    E --> F[Athena Query<br>SQL over Data Catalog]
    F -->|Results| G[S3 Athena Results<br>/athena-results/]

    subgraph StepFunctions[Step Functions Workflow]
        B
        D
        F
        H[Success State]
    end

    B --> D --> F --> H

🔧 How to Explain This

Producer (your Python script) calls Weather API.

Lambda ETL normalizes JSON and pushes to S3.

Glue Crawler auto-detects schema and updates Glue Data Catalog.

Athena queries the catalog → results saved back to S3.

Step Functions orchestrates the order: Lambda → Crawler → Athena → Success.
