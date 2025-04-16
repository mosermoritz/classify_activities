import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

def get_access_token() -> str:
    """
    Fetches a new access token from Strava using the refresh token.

    Returns:
        str: Access token for authenticated API requests

    Raises:
        Exception: If the token could not be fetched
    """
    response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': REFRESH_TOKEN
        }
    )
    data = response.json()

    if "access_token" not in data:
        raise Exception(f"❌ Failed to fetch token: {data}")

    return data['access_token']
