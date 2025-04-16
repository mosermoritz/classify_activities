from pathlib import Path

from datetime import datetime, timedelta
import pytest, requests, ast
from classify_activities.strava_client import get_access_token
from classify_activities.strava_utils import is_commute, mark_activity_as_commute, hide_activity_from_home

@pytest.mark.connection
def test_get_access_token_success():
    token = get_access_token()
    assert isinstance(token, str)
    assert len(token) > 20  # einfache Plausibilitätsprüfung



@pytest.mark.classify
def test_create_and_read_activity():
    token = get_access_token()

    # 1. Aktivität erstellen
    create_url = "https://www.strava.com/api/v3/activities"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": "🧪 Testaktivität – nur lesen",
        "type": "Workout",
        "start_date_local": "2025-04-14T10:00:00Z",
        "elapsed_time": 60,  # in Sekunden
        "description": "Nur zum Testen angelegt",
        "distance": 0,
        "private": 0
    }

    print("🚀 Lege Testaktivität an...")
    create_response = requests.post(create_url, headers=headers, data=payload)
    data = create_response.json()

    if create_response.status_code != 201:
        print("❌ Fehler beim Erstellen der Aktivität:", create_response.text)
        return

    activity_id = data["id"]
    activity_name = data["name"]

    print(f"✅ Aktivität erstellt: ID {activity_id}, Name: {activity_name}")

    # 2. Aktivität zurücklesen
    read_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    read_response = requests.get(read_url, headers=headers)

    if read_response.status_code != 200:
        print("❌ Fehler beim Abrufen der Aktivität:", read_response.text)
        return

    read_data = read_response.json()
    print("📋 Gelesene Aktivität:")
    print(f"🔹 ID: {read_data['id']}")
    print(f"🏷️ Name: {read_data['name']}")
    print(f"🔒 Privat: {'Ja' if read_data['private'] else 'Nein'}")
    print(f"📅 Datum: {read_data['start_date_local']}")

    # 3. Vergleich
    same = activity_id == read_data["id"] and activity_name == read_data["name"]
    print(f"✅ Vergleich: {'Identisch ✅' if same else 'Unterschiedlich ❌'}")



@pytest.mark.classify
def test_hide_activity_from_home():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a test activity
    create_response = requests.post(
        url="https://www.strava.com/api/v3/activities",
        headers=headers,
        data={
            "name": "Test Activity – hide from feed",
            "type": "Workout",
            "start_date_local": "2025-04-15T10:00:00Z",
            "elapsed_time": 120,
            "description": "Test: hide from home feed",
            "distance": 0,
            "private": 0
        }
    )

    assert create_response.status_code == 201, f"❌ Failed to create activity: {create_response.text}"
    activity = create_response.json()
    activity_id = activity["id"]
    print(f"✅ Created test activity with ID: {activity_id}")

    # 2. Hide from feed
    success = hide_activity_from_home(token, activity_id)
    assert success is True, "❌ hide_activity_from_home() failed"

    # 3. Verify it is hidden
    verify_response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers=headers
    )
    assert verify_response.status_code == 200, f"❌ Failed to fetch activity: {verify_response.text}"
    assert verify_response.json()["hide_from_home"] is True, "❌ Activity still visible in feed"

    print(f"✅ Activity {activity_id} is now hidden from home feed.")



@pytest.mark.classify
def test_mark_activity_as_commute():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Aktivität erstellen – 5 km "Ride"
    create_response = requests.post(
        url="https://www.strava.com/api/v3/activities",
        headers=headers,
        data={
            "name": "🚲 Testfahrt zur Arbeit",
            "type": "Ride",
            "start_date_local": "2025-04-15T07:30:00Z",
            "elapsed_time": 900,  # 15 Minuten
            "description": "Wird als Commute getaggt",
            "distance": 5000,  # 5 km
            "commute": 0
        }
    )

    assert create_response.status_code == 201, f"❌ Fehler beim Erstellen: {create_response.text}"
    activity = create_response.json()
    activity_id = activity["id"]
    assert not activity["commute"], "🚨 Aktivität war unerwartet bereits als Commute markiert"
    print(f"✅ Testaktivität erstellt mit ID: {activity_id}")

    # 2. Commute setzen – über eigene Funktion (kommt gleich)
    success = mark_activity_as_commute(token, activity_id)
    assert success is True, "❌ mark_activity_as_commute() war nicht erfolgreich"

    # 3. Abrufen und prüfen
    verify_response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers=headers
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["commute"] is True, "❌ Aktivität ist nicht als Commute markiert"
    print(f"✅ Aktivität {activity_id} wurde erfolgreich als Commute getaggt.")

@pytest.mark.classify
def load_test_activities(filename="test_activities.txt"):
    path = Path('test_activities.txt').parent / filename
    with open(path, "r") as f:
        content = f.read()
    return ast.literal_eval(content)

@pytest.mark.classify
def test_is_commute():
    activitys =load_test_activities()
    commutes = []
    for activity in activitys:
        if is_commute(activity) == True:
            commutes.append(activity)
    len_commutes = len(commutes)
    assert len_commutes == 3




@pytest.mark.classify
def test_hide_walk_from_home():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Dynamische Startzeit, um Duplikate zu vermeiden
    start_time = (datetime.utcnow() + timedelta(minutes=3)).isoformat() + "Z"

    # 1. Walk-Aktivität erstellen
    create_response = requests.post(
        url="https://www.strava.com/api/v3/activities",
        headers=headers,
        data={
            "name": "🚶 Spaziergang-Test",
            "type": "Walk",
            "start_date_local": start_time,
            "elapsed_time": 600,
            "description": "Test: hide_from_home bei Walk",
            "distance": 1000
        }
    )

    assert create_response.status_code == 201, f"❌ Fehler beim Erstellen: {create_response.text}"
    activity = create_response.json()
    activity_id = activity["id"]
    print(f"✅ Walk-Testaktivität erstellt mit ID: {activity_id}")

    # 2. hide_from_home setzen
    success = hide_activity_from_home(token, activity_id)
    assert success is True, "❌ hide_activity_from_home() fehlgeschlagen"

    # 3. Verifizieren
    verify_response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers=headers
    )
    assert verify_response.status_code == 200, f"❌ Fehler beim Abrufen: {verify_response.text}"
    assert verify_response.json()["hide_from_home"] is True, "❌ Walk ist noch im Feed sichtbar"

    print(f"✅ Walk-Aktivität {activity_id} ist jetzt korrekt aus dem Feed verborgen.")


@pytest.mark.classify
def test_hide_yoga_from_home():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Startzeit ein paar Minuten in der Zukunft
    start_time = (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z"

    # 1. Yoga-Aktivität erstellen
    create_response = requests.post(
        url="https://www.strava.com/api/v3/activities",
        headers=headers,
        data={
            "name": "🧘 Yoga-Test",
            "type": "Workout",
            "sport_type": "Yoga",
            "start_date_local": start_time,
            "elapsed_time": 900,
            "description": "Test für Yoga hide_from_home",
            "distance": 0
        }
    )

    assert create_response.status_code == 201, f"❌ Fehler beim Erstellen: {create_response.text}"
    activity = create_response.json()
    activity_id = activity["id"]
    print(f"✅ Yoga-Testaktivität erstellt mit ID: {activity_id}")

    # 2. hide_from_home setzen
    success = hide_activity_from_home(token, activity_id)
    assert success is True, "❌ hide_activity_from_home() fehlgeschlagen"

    # 3. Verifizieren
    verify_response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers=headers
    )
    assert verify_response.status_code == 200, f"❌ Fehler beim Abrufen: {verify_response.text}"
    assert verify_response.json()["hide_from_home"] is True, "❌ Yoga-Aktivität ist noch im Feed sichtbar"

    print(f"✅ Yoga-Aktivität {activity_id} ist jetzt korrekt aus dem Feed verborgen.")
