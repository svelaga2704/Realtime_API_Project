import json
import boto3
import base64
import os
from datetime import datetime, timezone

# S3 client
s3 = boto3.client("s3")

# Environment variable for bucket name
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")

def lambda_handler(event, context):
    for record in event["Records"]:
        # Decode Kinesis payload
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        print("📥 Raw payload:", payload)

        try:
            raw_data = json.loads(payload)

            # If "data" is a string, parse it again
            if isinstance(raw_data.get("data"), str):
                try:
                    raw_data["data"] = json.loads(raw_data["data"].replace("'", '"'))
                except Exception as e:
                    print("❌ Failed to parse nested data:", str(e))

            print("✅ Parsed data:", raw_data)

            # --- Transformation / Cleaning Logic ---
            weather = raw_data.get("data", {})

            cleaned_data = {
                "city": weather.get("location", {}).get("name"),
                "country": weather.get("location", {}).get("country"),
                "temperature_c": weather.get("current", {}).get("temp_c"),
                "humidity": weather.get("current", {}).get("humidity"),
                "condition": weather.get("current", {}).get("condition", {}).get("text"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            print("🧹 Cleaned data:", cleaned_data)

            # --- Save to S3 ---
            file_name = f"weather-data-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"

            s3.put_object(
                Bucket=S3_BUCKET,
                Key=f"raw/{file_name}",
                Body=json.dumps(cleaned_data)
            )

            print(f"✅ Saved to S3: {S3_BUCKET}/raw/{file_name}")

        except Exception as e:
            print("❌ Error processing record:", str(e))

    return {
        "statusCode": 200,
        "body": json.dumps("Weather data processed successfully!")
    }
