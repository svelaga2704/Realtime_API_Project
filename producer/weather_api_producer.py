import os
import boto3
import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
STREAM_NAME = os.getenv("STREAM_NAME")
REGION = os.getenv("REGION")
LOCATION = os.getenv("LOCATION")

kinesis_client = boto3.client("kinesis", region_name=REGION)

def get_weather():
    """Fetch weather data from WeatherAPI"""
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={LOCATION}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch weather: {response.text}")
        return None

def send_to_kinesis(weather_data):
    """Send weather JSON to Kinesis"""
    try:
        payload = {
            "location": LOCATION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": weather_data
        }

        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(payload),
            PartitionKey="partitionKey-weather"
        )

        print("✅ Successfully sent to Kinesis:", response)

    except Exception as e:
        print("❌ Error sending to Kinesis:", str(e))

if __name__ == "__main__":
    weather = get_weather()
    if weather:
        send_to_kinesis(weather)
