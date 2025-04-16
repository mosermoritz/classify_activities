import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from classify_activities.strava_client import get_access_token

# Load environment variables from .env
load_dotenv()

# --- API Helpers ---

def get_recent_activities(access_token: str, days: int = 30) -> list:
    """
    Returns all activities from the last X days.

    Args:
        access_token (str): Valid Strava access token
        days (int): Number of days to look back

    Returns:
        list: List of activity dictionaries
    """
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    after = int((datetime.now() - timedelta(days=days)).timestamp())

    response = requests.get(url, headers=headers, params={"per_page": 100, "after": after})
    if response.status_code != 200:
        print(f"❌ Failed to fetch activities: {response.text}")
        return []

    return response.json()

def mark_activity_as_commute(access_token: str, activity_id: int) -> bool:
    """
    Marks an activity as a commute.

    Returns:
        bool: True if update was successful
    """
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"commute": "1"}
    response = requests.put(url, headers=headers, data=data)
    return response.status_code == 200

def hide_activity_from_home(access_token: str, activity_id: int) -> bool:
    """
    Hides an activity from appearing in followers' home feed.

    Returns:
        bool: True if update was successful
    """
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"hide_from_home": "true"}
    response = requests.put(url, headers=headers, data=data)
    return response.status_code == 200

# --- Classification Rules ---

def is_commute(activity: dict) -> bool:
    """
    Determines whether a Ride activity is a commute based on:
    - Type is Ride
    - Distance ≤ 10 km
    - Device is Garmin
    - Not from MyWhoosh

    Returns:
        bool: True if likely a commute
    """
    if activity.get("type") != "Ride":
        return False

    if activity.get("distance", 0) / 1000 > 10:
        return False

    device = activity.get("device_name", "").lower()
    if "garmin" not in device and device != "":
        return False

    if activity.get("name", "").startswith("MyWhoosh"):
        return False

    return True

def is_walking(activity: dict) -> bool:
    return activity.get("type") == "Walk"

def is_yoga(activity: dict) -> bool:
    return activity.get("type") == "Yoga"

# --- Main Automation ---

def classify_recent_activities(days: int = 1):
    """
    Classifies and updates recent Strava activities.

    - Tags commute rides
    - Hides commutes, walks, and yoga from followers' home feed
    """
    token = get_access_token()
    activities = get_recent_activities(token, days)

    for activity in activities:
        activity_id = activity["id"]
        name = activity.get("name", "Unnamed")
        act_type = activity.get("type", "Unknown")

        print(f"\n🔍 Checking: {name} ({act_type})")

        if is_commute(activity):
            print("🚲 Marking as commute and hiding from feed...")
            mark_activity_as_commute(token, activity_id)
            hide_activity_from_home(token, activity_id)

        elif is_walking(activity) or is_yoga(activity):
            print("🧘 Hiding walk/yoga from feed...")
            hide_activity_from_home(token, activity_id)

if __name__ == "__main__":
    classify_recent_activities()
