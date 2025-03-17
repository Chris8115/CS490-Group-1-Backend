# CS490 Group 1 Backend

## Setup
- Create/activate python venv `python -m venv venv`
- (in venv) `pip install -r requirements.txt`
- `python app.py`

## API
### Users
- `/users` (GET)
   - example: `/users?first_name=birch&user_id=10` includes users whose names contain "birch" or have a user_id of 10
- Gets all of the users from the `users` table with optional filters.
- Returns `users` array in json.
- Optional Parameters (can be combined)
   - first_name: includes results like `first_name` column
   - last_name: includes results like `last_name` column
   - user_id: includes results matching `user_id` column
   - role: includes results matching `role` column (pharmacist, doctor, or patient)

### Doctors
- Gets all of the doctors from the `doctors` table with optional filters.
- Returns `doctors` array in json.
- Optional Parameters (can be combined)
   - specialization: includes results like `specialization` column
   - license_number: includes results matching `license_number` column
   - doctor_id: includes results matching `doctor_id` column

### Patients
- Gets all of the patients from the `patients` table with optional filters.
- Returns `patients` array in json.
- Optional Parameter
   - patient_id: includes results matching `patient_id` column
