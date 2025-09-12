import boto3
import os
import json
import base64
from datetime import datetime, timezone   # ✅ import timezone

# Initialize S3 client
s3 = boto3.client("s3")

# Get bucket from environment variable (or default if not set)
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "praneeth-weather-data")

def lambda_handler(event, context):
    print("Incoming event:", json.dumps(event))

    payload = None

    # Case 1: Event from Step Functions (direct JSON)
    if "Records" not in event:
        payload = json.dumps(event)  # Use event directly as JSON string
        print("Step Functions payload:", payload)

    # Case 2: Event from Kinesis stream
    else:
        for record in event["Records"]:
            try:
                payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
                print("Kinesis payload:", payload)
            except Exception as e:
                print("❌ Failed to decode Kinesis record:", str(e))
                continue

    if not payload:
        raise ValueError("No payload found to process")

    # Create unique file name with timestamp (UTC-aware)
    file_name = f"weather-data-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"

    # Upload raw payload to S3
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"raw/{file_name}",
        Body=payload
    )

    print(f"✅ Saved file {file_name} to S3 bucket {S3_BUCKET}/raw/")

    return {
        "status": "success",
        "bucket": S3_BUCKET,
        "file": file_name
    }
