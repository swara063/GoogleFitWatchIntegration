import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/fitness.activity.read"]

def authenticate_google_fit(json_path):
    """Step 1: Generate Google Fit Authentication URL"""
    flow = Flow.from_client_secrets_file(
        json_path,
        scopes=SCOPES,
        redirect_uri="https://your-streamlit-app-url"  # Update after deployment
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent')
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
        try:
            dataset = service.users().dataset().aggregate(
                userId="me",
                body={
                    "aggregateBy": [{"dataTypeName": data_type}],
                    "bucketByTime": {"durationMillis": 86400000},  # Last 24 hours
                    "startTimeMillis": "0",
                    "endTimeMillis": "9999999999999"
                }
            ).execute()

            results[key] = dataset.get("bucket", [{}])[0].get("dataset", [{}])[0].get("point", [{}])[0].get("value", [{}])
        except Exception as e:
            results[key] = f"Error: {e}"

    return results



    data = service.users().dataSources().list(userId="me").execute()
    return data
