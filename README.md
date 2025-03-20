# CS490 Group 1 Backend

## Setup
- Create/activate python venv `python -m venv venv`
- (in venv) `pip install -r requirements.txt`
- `python app.py`
- Note: Only commit schema changes to the database `craze.db`, try not to add it to your commit otherwise since it is practically always changing since the entire database is in that file. It's intentionally not added to the `.gitignore` since it may be necessary sometimes. (Also, if you do make changes to the schema, add a backup like `craze.db.bak`)

## API
### Users
- `/users` (GET)
- Gets all of the users from the `users` table with optional filters.
   - example: `/users?first_name=birch&user_id=10` includes users whose names contain "birch" or have a user_id of 10
- Returns `users` array in json.
- Optional Parameters (can be combined)
   - first_name: includes results like `first_name` column
   - last_name: includes results like `last_name` column
   - user_id: includes results matching `user_id` column
   - role: includes results matching `role` column (pharmacist, doctor, or patient)
- Note: passwords are omitted for security reasons. 

### Doctors
- `/doctors` (GET)
- Gets all of the doctors from the `doctors` table with optional filters.
   - example: `/doctors?specialization=physician` includes doctors whose specializations contain "physician"
- Returns `doctors` array in json.
- Optional Parameters (can be combined)
   - specialization: includes results like `specialization` column
   - license_number: includes results matching `license_number` column
   - doctor_id: includes results matching `doctor_id` column

### Patients
- `/patients` (GET)
- Gets all of the patients from the `patients` table with optional filters.
   - example: `/patients?patient_id=2` includes patient with id of 2
- Returns `patients` array in json.
- Optional Parameters
   - patient_id: includes results matching `patient_id` column

### Appointments
- `/appointments` (GET)
- Gets all of the appointments from the `appointments` table with optional filters.
   - example: `/appointments?status=accepted&reason=surgery` includes all accepted appointments for reasons containing "surgery"
- Returns `appointments` array in json.
- Optional Parameters
   - appointment_id: includes results matching `appointment_id` column
   - doctor_id: includes results matching `doctor_id` column
   - patient_id: includes results matching `patient_id` column
   - status: includes results matching `status` column (accepted, rejected, pending, canceled)
   - reason: includes results like `reason` column

### Forum Posts
- `/forum_posts` (GET)
- Gets all of the forum posts from the `forum_posts` table with optional filters.
   - example: `/forum_posts?post_type=exercise+plan&title=upper+body` includes all exercise posts with titles containing "upper body"
- Returns `forum_posts` array in json.
- Optional Parameters
   - post_id: includes results matching `post_id` column
   - user_id: includes results matching `user_id` column
   - title: includes results like `title` column
   - post_type: includes results like `post_type` column (exercise plan, discussion)

#### Reviews
- `/reviews` (GET)
  Retrieves all reviews from the `reviews` table with optional filters.
   - example: `/reviews?doctor_id=1&rating=5` Returns reviews for doctor 1 that have a rating of 5.
- Returns a JSON array named `reviews`.
- Optional Parameters
  - review_id: Filters results matching the `review_id` column.
  - doctor_id: Filters results matching the `doctor_id` column.
  - patient_id: Filters results matching the `patient_id` column.
  - rating: Filters results matching the `rating` column (typically values 1–5).
  - review_text: Performs a text search on the `review_text` column.