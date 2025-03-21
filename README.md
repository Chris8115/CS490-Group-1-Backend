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

### Pharmacists
- `/pharmacists` (GET)
- Gets all of the pharmacies from the `pharmacists` table with optional filters.
   - example: `/pharmacists?pharmacy_location=springview` includes all pharmacies with locations containing "springview"
- Returns `pharmacists` array in json.
- Optional Parameters (can be combined)
   - pharmacist_id: includes results matching `pharmacist_id` column
   - pharmacy_location: includes results like `pharmacy_location` column

### Appointments
- `/appointments` (GET)
- Gets all of the appointments from the `appointments` table with optional filters.
   - example: `/appointments?status=accepted&reason=surgery` includes all accepted appointments for reasons containing "surgery"
- Returns `appointments` array in json.
- Optional Parameters (can be combined)
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
- Optional Parameters (can be combined)
   - post_id: includes results matching `post_id` column
   - user_id: includes results matching `user_id` column
   - title: includes results like `title` column
   - post_type: includes results like `post_type` column (exercise plan, discussion)

### Forum Comments
- `/forum_comments` (GET)
- Gets all of the post comments from the `forum_comments` table with optional filters.
   - example: `/forum_comments?post_id=1` includes all comments under the post with post_id = 1
- Returns `forum_comments` array in json.
- Optional Parameters (can be combined)
   - comment_id: includes results matching `comment_id` column
   - post_id: includes results matching `post_id` column
   - user_id: includes results matching `user_id` column

### Reviews
- `/reviews` (GET)
- Retrieves all reviews from the `reviews` table with optional filters.
   - example: `/reviews?doctor_id=1&rating=5` Returns reviews for doctor 1 that have a rating of 5.
- Returns a JSON array named `reviews`.
- Optional Parameters (can be combined)
  - review_id: Filters results matching the `review_id` column.
  - doctor_id: Filters results matching the `doctor_id` column.
  - patient_id: Filters results matching the `patient_id` column.
  - rating: Filters results matching the `rating` column (typically values 1–5).
  - review_text: Performs a text search on the `review_text` column.

### Addresses
- `/address` (GET)
- Gets all of the addresses from the `address` table with optional filters.
   - example: `/address?city=phoenix` includes all addresses from the city of phoenix.
- Returns `address` array in json.
- Optional Parameters (can be combined)
   - address_id: includes results matching `address_id` column
   - city: includes results like `city` column
   - address: includes results like `address` column
   - address2: includes results like `address2` column
   - zip: includes results matching `zip` column

### Credit Cards
- `/credit_card` (GET)
- Gets all of the credit cards from the `credit_card` table with optional filters.
   - example: `/credit_card?card_ending=2088` gets credit card that ends in x2088
- Returns `credit_card` array in json.
- Optional Parameters (can be combined)
   - creditcard_id: includes results matching `creditcard_id` column
   - card_ending: includes results with `cardnumber` ending in `card_ending` **(length must be <= 4)**
   - exp_date: includes results like `exp_date` column

### Doctor Patient Relationships
- `/doctor_patient_relationship` (GET)
- Gets all of the doctor patient relationships from the `doctor_patient_relationship` table with optional filters.
   - example: `/doctor_patient_relationship?status=pending` gets all relationships with pending statuses
- Returns `doctor_patient_relationship` array in json.
- Optional Parameters (can be combined)
   - doctor_id: includes results matching `doctor_id` column
   - patient_id: includes results matching `patient_id` column
   - status: includes results like `status` column (active, inactive, pending)

### Exercise Plans
- `/exercise_plans` (GET)
- Gets all of the exercise plans from the `exercise_plans` table with optional filters.
   - example: `/exercise_plans?title=push-up` gets all exercise plans with titles including "push-up"
- Returns `exercise_plans` array in json.
- Optional Parameters (can be combined)
   - exercise_id: includes results matching `exercise_id` column
   - title: includes results like `title` column
