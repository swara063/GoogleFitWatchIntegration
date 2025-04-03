import json
import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Google Fit Scopes (Modify if needed)
SCOPES = ["https://www.googleapis.com/auth/fitness.activity.read"]

def authenticate_google_fit(client_secrets_file):
    """Step 1: Generate Google Fit Authentication URL"""
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=SCOPES,
        redirect_uri="https://your-deployed-streamlit-app.com"  # Update to your actual Streamlit app URL
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type="offline")
    return auth_url, flow

def fetch_google_fit_token(auth_code, flow):
    """Step 2: Exchange Auth Code for Google Fit Token"""
    flow.fetch_token(code=auth_code)
    creds = flow.credentials
    return json.loads(creds.to_json())

def fetch_google_fit_data(credentials_json):
    """Step 3: Fetch Google Fit Data"""
    creds = Credentials.from_authorized_user_info(credentials_json)
    service = build("fitness", "v1", credentials=creds)

    # Get timestamp for last 24 hours
    now = datetime.datetime.utcnow()
    start_time = int((now - datetime.timedelta(days=1)).timestamp() * 1000)
    end_time = int(now.timestamp() * 1000)

    # Define the list of required data types
    data_types = {
        "Heart Rate": "com.google.heart_rate.bpm",
        "Blood Pressure": "com.google.blood_pressure",
        "SpO2 (Oxygen)": "com.google.oxygen_saturation",
        "Steps": "com.google.step_count.delta",
        "Calories": "com.google.calories.expended",
        "Sleep": "com.google.sleep.segment"
    }

    results = {}

    for key, data_type in data_types.items():
        request = service.users().dataset().aggregate(
            userId="me",
            body={
                "aggregateBy": [{"dataTypeName": data_type}],
                "bucketByTime": {"durationMillis": 86400000},  # 24 hours
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
        ).execute()

        data_points = request.get("bucket", [{}])[0].get("dataset", [{}])[0].get("point", [])

        if data_points:
            results[key] = data_points[0].get("value", [{}])
        else:
            results[key] = "No Data"

    return results


