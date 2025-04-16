from strava_client import get_access_token
from strava_utils import (
    get_recent_activities,
    is_commute,
    is_walking,
    is_yoga,
    mark_activity_as_commute,
    hide_activity_from_home,
)

def classify_recent_activities(days: int = 1):
    """
    Classifies and processes recent Strava activities.

    - Tags rides as commute if distance and type match.
    - Hides walks, yoga, and commute rides from home feed.
    """
    token = get_access_token()
    activities = get_recent_activities(token, days=days)

    for activity in activities:
        activity_id = activity["id"]
        name = activity.get("name", "Unnamed")
        act_type = activity.get("type")

        print(f"\n🔍 Processing activity: {name} ({act_type})")

        if "mywhoosh" in name.lower():
            print("⏩ Skipped MyWhoosh virtual ride.")
            continue

        # Commute detection and tagging
        if is_commute(activity):
            print("🚲 Detected as commute.")
            mark_activity_as_commute(token, activity_id)
            hide_activity_from_home(token, activity_id)
            continue

        # Walk/Yoga hiding
        if is_walking(activity) or is_yoga(activity):
            print("🧘 Detected as walk or yoga — hiding.")
            hide_activity_from_home(token, activity_id)

if __name__ == "__main__":
    classify_recent_activities()
