import requests

BASE_URL = "http://localhost:5000"
TEST_EMAILS = ["Eugene.Krabs@krustykrab.com", "Sponge.Bob@krustykrab.com"]

def get_user_id_by_email(email):
    res = requests.get(f"{BASE_URL}/users", params={"email": email})
    if res.status_code == 200:
        users = res.json().get("users", [])
        if users:
            return users[0]['user_id']
    return None

def delete_user(user_id):
    return requests.delete(f"{BASE_URL}/users/{user_id}")

# Runs before any tests
def pytest_sessionstart(session):
    print("\n[Prerun] Cleaning up test users before suite starts...")
    delete_latest_review_for_doctor(1)
    for email in TEST_EMAILS:
        user_id = get_user_id_by_email(email)
        if user_id:
            # Remove any doctor-patient relationship involving this user
            for other_email in TEST_EMAILS:
                other_id = get_user_id_by_email(other_email)
                if other_id and other_id != user_id:
                    requests.delete(f"{BASE_URL}/doctor_patient_relationship/{1}/{user_id}")

            res = delete_user(user_id)
            print(f"[Prerun] Deleted user {user_id} ({email}): {res.status_code}")


# Runs after all tests
def pytest_sessionfinish(session, exitstatus):
    delete_latest_review_for_doctor(1)
    delete_latest_review_for_doctor(1)
    delete_latest_appointment_and_transaction()

    print("\n[Postrun] Cleaning up test users after suite ends...")
    for email in TEST_EMAILS:
        user_id = get_user_id_by_email(email)
        if user_id:
            # Try removing doctor-patient relationship with both roles
            for other_email in TEST_EMAILS:
                other_id = get_user_id_by_email(other_email)
                if other_id and other_id != user_id:
                    # Try deleting both patient-doctor and doctor-patient combos
                    requests.delete(f"{BASE_URL}/doctor_patient_relationship/{1}/{user_id}")
            
            res = delete_user(user_id)
            print(f"[Postrun] Deleted user {user_id} ({email}): {res.status_code}")

def delete_latest_review_for_doctor(doctor_id):
    res = requests.get(f"{BASE_URL}/reviews", params={"doctor_id": doctor_id})
    if res.status_code == 200:
        reviews = res.json().get("reviews", [])
        if reviews:
            latest_review = sorted(reviews, key=lambda r: r["review_id"], reverse=True)[0]
            review_id = latest_review["review_id"]
            del_res = requests.delete(f"{BASE_URL}/reviews/{review_id}")
            print(f"Deleted review {review_id} for doctor {doctor_id}: {del_res.status_code}")

def delete_latest_appointment_and_transaction():
    try:
        session = get_authenticated_session()
        res = session.get(f"{BASE_URL}/appointments")
        if res.status_code == 200:
            appointments = res.json().get("appointments", [])
            if appointments:
                latest = max(appointments, key=lambda a: a["appointment_id"])
                appt_id = latest["appointment_id"]

                tx_res = session.delete(f"{BASE_URL}/transactions/{appt_id}")
                print(f"[Postrun] Deleted transaction {appt_id}: {tx_res.status_code}")

                appt_res = session.delete(f"{BASE_URL}/appointments/{appt_id}")
                print(f"[Postrun] Deleted appointment {appt_id}: {appt_res.status_code}")
    except Exception as e:
        print(f"[Postrun] Error during appointment cleanup: {e}")

def get_authenticated_session():
    session = requests.Session()
    login_data = {
        "email": "Eugene.Krabs@krustykrab.com",
        "password": "password"
    }
    res = session.post(f"{BASE_URL}/login", json=login_data)
    if res.status_code == 200:
        return session
    raise Exception("Login failed for cleanup")


