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

