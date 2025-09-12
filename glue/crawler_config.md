# AWS Glue Crawler Configuration

## 📌 Crawler Name
`weather-data-crawler`

---

## 🏗️ Purpose
The crawler scans the **S3 bucket** where the Lambda function (`etl-weather-transform`) stores weather data.  
It infers the schema and updates the **AWS Glue Data Catalog**, making the data queryable in **Amazon Athena**.

---

## ⚙️ Configuration Details

- **Crawler Name:** `weather-data-crawler`
- **IAM Role:** `AWSGlueServiceRole` (must allow read access to S3 and write access to Glue Data Catalog)
- **Data Store:**
  - **Type:** S3
  - **Path:** `s3://praneeth-weather-data/raw/`
- **Glue Database:** `weather_db`
  - Created during crawler setup
  - Stores the metadata tables
- **Tables Generated:**
  - Example: `weather_data_jsonraw`
  - Schema is auto-detected from JSON files
- **Schedule:** On-demand (can be run manually or via Step Functions)

---

## 🔄 Workflow
1. **Lambda Function:**  
   `etl-weather-transform` writes cleaned JSON weather data to:

2. **Crawler:**  
`weather-data-crawler` scans the above S3 path.

3. **Glue Data Catalog:**  
The schema is inferred and stored in the `weather_db` database.

4. **Athena Queries:**  
Using Athena, we can query the table created by the crawler.

---

## 📝 Example Athena Query
```sql
SELECT 
city,
country,
temperature_c,
humidity,
condition,
timestamp
FROM weather_db.weather_data_jsonraw
LIMIT 10;

## ✅ Notes

Ensure the IAM role attached to the crawler has AmazonS3ReadOnlyAccess and AWSGlueServiceRole policies.

The crawler should be re-run whenever new files land in the S3 bucket.

This crawler is part of the overall pipeline:
Producer → Kinesis → Lambda → S3 → Glue Crawler → Athena → Step Functions