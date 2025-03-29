# CS490 Group 1 Backend

## Setup
- Create/activate python venv `python -m venv venv`
- (in venv) `pip install -r requirements.txt`
- `python app.py`
> [!NOTE]  
> Only commit schema changes to the database `craze.db`, try not to add it to your commit otherwise since it is practically always changing since the entire database is in that file. It's intentionally not added to the `.gitignore` since it may be necessary sometimes. (Also, if you do make changes to the schema, add a backup like `craze.db.bak`)

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

- `/reviews` (PUT)
- Updates an existing review in the `reviews` table.
   - example: `/reviews` with a JSON body containing updated fields.
- Request Body (JSON):
  - review_id: **Required.** The ID of the review to update.
  - rating: *(Optional)* New numeric rating (typically values 1–5).
  - review_text: *(Optional)* New review text.
- Returns a confirmation message in JSON indicating that the review was updated successfully.

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
   - exp_date: includes results like `exp_date` column (A date of format mm/dd/yyyy)

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

### Inventory
- `/inventory` (GET)
- Gets all of the inventory entries from the `inventory` table with optional filters.
   - example: `/inventory?inventory_id=5` gets inventory entry with id of 5
- Returns `inventory` array in json.
- Optional Parameters (can be combined)
   - inventory_id: includes results matching `inventory_id` column
   - medication_id: includes results matching `medication_id` column

### Medications
- `/medications` (GET)
- Gets all of the medication entries from the `medications` table with optional filters.
   - example: `/medications?name=nutrislim` gets the medication with name "NutriSlim"
- Returns `medications` array in json.
- Optional Parameters (can be combined)
   - medication_id: includes results matching `medication_id` column
   - name: includes results like `name` column

### Patient Exercise Assignments
- `/patient_exercise_assignments` (GET)
- Gets all of the patient exercise assignment entries from the `patient_exercise_assignments` table with optional filters.
   - example: `/patient_exercise_assignments?doctor_id=4&patient_id=5` gets all assignments from the doctor with `doctor_id` = 4 and the patient with `patient_id` = 5
- Returns `patient_exercise_assignments` array in json.
- Optional Parameters (can be combined)
   - assignment_id: includes results matching `assignment_id` column
   - patient_id: includes results matching `patient_id` column
   - doctor_id: includes results matching `doctor_id` column
   - exercise_id: includes results matching `exercise_id` column
   - assigned_at: includes results like `assigned_at` column (A date of format mm/dd/yyyy)

### Patient Progress
- `/patient_progress` (GET)
- Gets all of the patient progress reports from the `patient_progress` table with optional filters.
   - example: `/patient_progress?date_logged=2025-03-06&patient_id=2` gets the progress report for patient with an id = 2 on March 6th, 2025.
- Returns `patient_progress` array in json.
- Optional Parameters (can be combined)
   - progress_id: includes results matching `progress_id` column
   - patient_id: includes results matching `patient_id` column
   - date_logged: includes results like `date_logged` column (A datetime of format mm-dd-yyyy hh:mm:ss)

### Prescriptions
- `/prescriptions` (GET)
- Gets all of the prescriptions from the `prescriptions` table with optional filters.
   - example: `/prescriptions?pharmacist_id=6&status=accepted` gets all Accepted prescriptions from the pharmacy with an id = 6
- Returns `prescriptions` array in json.
- Optional Parameters (can be combined)
   - prescription_id: includes results matching `prescription_id` column
   - doctor_id: includes results matching `doctor_id` column
   - medication_id: includes results matching `medication_id` column
   - patient_id: includes results matching `patient_id` column
   - pharmacist_id: includes results matching `pharmacist_id` column
   - status: includes results like `status` column (canceled, rejected, accepted, ready)
   - date_prescribed: includes results like `date_prescribed` column (A datetime of format mm-dd-yyyy hh:mm:ss)

### Saved Posts
- `/saved_posts` (GET)
- Gets all of the discussion posts users have saved from the `saved_posts` table with optional filters.
   - example: `/saved_posts?user_id=11&saved_at=2025` gets all of the posts the user with an id = 11 saved in the year 2025.
- Returns `saved_posts` array in json.
- Optional Parameters (can be combined)
   - post_id: includes results matching `post_id` column
   - user_id: includes results matching `user_id` column
   - saved_at: includes results like `saved_at` column (A datetime of format mm-dd-yyyy hh:mm:ss)

### Transactions
- `/transactions` (GET)
- Gets all of the transaction records from the `transactions` table with optional filters.
   - example: `/transactions?creditcard_id=3` gets all transactions paid for by a credit card with an id = 3
- Returns `transactions` array in json.
- Optional Parameters (can be combined)
   - creditcard_id: includes results matching `creditcard_id` column
   - patient_id: includes results matching `patient_id` column
   - doctor_id: includes results matching `doctor_id` column
   - transaction_id: includes results matching `transaction_id` column
   - created_at: includes results like `created_at` column (A date of format mm/dd/yyyy)