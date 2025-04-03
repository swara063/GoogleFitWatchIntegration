import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Path to Google OAuth credentials file
CLIENT_SECRETS_FILE = "client_secrets.json"

# Google Fit Scopes (Modify if needed)
SCOPES = ["https://www.googleapis.com/auth/fitness.activity.read"]

def authenticate_google_fit():
    """Step 1: Generate Google Fit Authentication URL"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
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

    data = service.users().dataSources().list(userId="me").execute()
    return data
