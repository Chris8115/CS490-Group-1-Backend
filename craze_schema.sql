BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "address" (
	"address_id"	INTEGER NOT NULL,
	"city"	TEXT NOT NULL,
	"country"	TEXT NOT NULL,
	"address2"	TEXT,
	"address"	TEXT NOT NULL,
	"zip"	INTEGER NOT NULL,
	CONSTRAINT "address_pk" PRIMARY KEY("address_id")
);
CREATE TABLE IF NOT EXISTS "appointments" (
	"appointment_id"	INTEGER NOT NULL,
	"doctor_id"	INTEGER,
	"patient_id"	INTEGER,
	"start_time"	TIMESTAMP NOT NULL,
	"end_time"	TIMESTAMP NOT NULL,
	"status"	TEXT NOT NULL,
	"location"	TEXT NOT NULL,
	"reason"	TEXT NOT NULL,
	"created_at"	TIMESTAMP NOT NULL,
	CONSTRAINT "appointments_pk" PRIMARY KEY("appointment_id"),
	CONSTRAINT "doctor_id" FOREIGN KEY("doctor_id") REFERENCES "users"("user_id"),
	CONSTRAINT "patient_id" FOREIGN KEY("patient_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "credit_card" (
	"creditcard_id"	INTEGER NOT NULL,
	"cardnumber"	INTEGER NOT NULL,
	"cvv"	INTEGER NOT NULL,
	"exp_date"	DATE NOT NULL,
	CONSTRAINT "credit_credit_pk" PRIMARY KEY("creditcard_id")
);
CREATE TABLE IF NOT EXISTS "doctor_patient_relationship" (
	"doctor_id"	INTEGER,
	"patient_id"	INTEGER,
	"status"	TEXT NOT NULL,
	"date_assigned"	TIMESTAMP NOT NULL,
	CONSTRAINT "doctor_id" FOREIGN KEY("doctor_id") REFERENCES "users"("user_id"),
	CONSTRAINT "patient_id" FOREIGN KEY("patient_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "doctors" (
	"doctor_id"	INTEGER NOT NULL,
	"license_number"	INTEGER NOT NULL,
	"specialization"	TEXT NOT NULL,
	"profile"	TEXT NOT NULL,
	PRIMARY KEY("doctor_id"),
	CONSTRAINT "doctor_id" FOREIGN KEY("doctor_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "exercise_plans" (
	"exercise_id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	CONSTRAINT "exercise_plans_pk" PRIMARY KEY("exercise_id")
);
CREATE TABLE IF NOT EXISTS "forum_comments" (
	"comment_id"	INTEGER NOT NULL,
	"post_id"	INTEGER,
	"user_id"	INTEGER,
	"comment_text"	TEXT NOT NULL,
	"created_at"	TIMESTAMP NOT NULL,
	CONSTRAINT "forum_comments_pk" PRIMARY KEY("comment_id"),
	CONSTRAINT "post_id" FOREIGN KEY("post_id") REFERENCES "forum_posts"("post_id"),
	CONSTRAINT "user_id" FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "forum_posts" (
	"post_id"	INTEGER NOT NULL,
	"user_id"	INTEGER,
	"title"	TEXT NOT NULL,
	"content"	TEXT NOT NULL,
	"post_type"	TEXT NOT NULL,
	"created_at"	TIMESTAMP NOT NULL,
	CONSTRAINT "forum_posts_pk" PRIMARY KEY("post_id"),
	CONSTRAINT "user_id" FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "inventory" (
	"inventory_id"	INTEGER NOT NULL,
	"medication_id"	INTEGER NOT NULL,
	"stock"	INTEGER NOT NULL,
	"last_updated"	TIMESTAMP NOT NULL,
	CONSTRAINT "inventory_pk" PRIMARY KEY("inventory_id"),
	CONSTRAINT "medication_id" FOREIGN KEY("medication_id") REFERENCES "medications"("medication_id")
);
CREATE TABLE IF NOT EXISTS "medications" (
	"medication_id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	CONSTRAINT "medications_pk" PRIMARY KEY("medication_id")
);
CREATE TABLE IF NOT EXISTS "patient_exercise_assignments" (
	"assignment_id"	INTEGER NOT NULL,
	"patient_id"	INTEGER,
	"doctor_id"	INTEGER,
	"assigned_at"	TIMESTAMP NOT NULL,
	"instructions"	TEXT NOT NULL,
	"exercise_id"	INTEGER NOT NULL,
	CONSTRAINT "patient_exercise_assignments_pk" PRIMARY KEY("assignment_id"),
	CONSTRAINT "doctor_id" FOREIGN KEY("doctor_id") REFERENCES "users"("user_id"),
	FOREIGN KEY("exercise_id") REFERENCES "exercise_plans"("exercise_id"),
	CONSTRAINT "patient_id" FOREIGN KEY("patient_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "patient_progress" (
	"progress_id"	INTEGER NOT NULL,
	"patient_id"	INTEGER,
	"date_logged"	TIMESTAMP NOT NULL,
	"weight"	REAL NOT NULL,
	"calories"	REAL NOT NULL,
	"notes"	TEXT,
	CONSTRAINT "patient_progress_pk" PRIMARY KEY("progress_id"),
	CONSTRAINT "patient_id" FOREIGN KEY("patient_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "patients" (
	"patient_id"	INTEGER NOT NULL,
	"address_id"	INTEGER NOT NULL,
	"medical_history"	TEXT NOT NULL,
	"creditcard_id"	INTEGER NOT NULL,
	PRIMARY KEY("patient_id"),
	CONSTRAINT "address_id" FOREIGN KEY("address_id") REFERENCES "address"("address_id"),
	CONSTRAINT "creditcard_id" FOREIGN KEY("creditcard_id") REFERENCES "credit_card"("creditcard_id"),
	CONSTRAINT "patient_id" FOREIGN KEY("patient_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "pharmacists" (
	"pharmacist_id"	INTEGER NOT NULL,
	"pharmacy_location"	TEXT NOT NULL,
	CONSTRAINT "pharmacists_pk" PRIMARY KEY("pharmacist_id")
);
CREATE TABLE IF NOT EXISTS "prescriptions" (
	"prescription_id"	INTEGER NOT NULL,
	"doctor_id"	INTEGER,
	"patient_id"	INTEGER,
	"medication_id"	INTEGER,
	"instructions"	TEXT NOT NULL,
	"date_prescribed"	TIMESTAMP NOT NULL,
	"status"	TEXT NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"pharmacist_id"	INTEGER NOT NULL,
	CONSTRAINT "prescriptions_pk" PRIMARY KEY("prescription_id"),
	FOREIGN KEY("doctor_id") REFERENCES "doctors"("doctor_id"),
	CONSTRAINT "medication_id" FOREIGN KEY("medication_id") REFERENCES "medications"("medication_id"),
	FOREIGN KEY("patient_id") REFERENCES "patients"("patient_id"),
	FOREIGN KEY("pharmacist_id") REFERENCES "pharmacists"("pharmacist_id")
);
CREATE TABLE IF NOT EXISTS "reviews" (
	"review_id"	INTEGER NOT NULL,
	"patient_id"	INTEGER,
	"doctor_id"	INTEGER,
	"rating"	INTEGER NOT NULL,
	"review_text"	TEXT,
	"created_at"	TIMESTAMP NOT NULL,
	CONSTRAINT "reviews_pk" PRIMARY KEY("review_id"),
	CONSTRAINT "doctor_id" FOREIGN KEY("doctor_id") REFERENCES "users"("user_id"),
	CONSTRAINT "patient_id" FOREIGN KEY("patient_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "saved_posts" (
	"user_id"	INTEGER,
	"post_id"	INTEGER,
	"saved_at"	TIMESTAMP NOT NULL,
	CONSTRAINT "post_id" FOREIGN KEY("post_id") REFERENCES "forum_posts"("post_id"),
	CONSTRAINT "user_id" FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TABLE IF NOT EXISTS "transactions" (
	"transaction_id"	INTEGER NOT NULL,
	"patient_id"	INTEGER,
	"doctor_id"	INTEGER,
	"service_fee"	REAL NOT NULL,
	"doctor_fee"	REAL NOT NULL,
	"subtotal"	REAL NOT NULL,
	"created_at"	TIMESTAMP NOT NULL,
	"creditcard_id"	INTEGER,
	CONSTRAINT "transactions_pk" PRIMARY KEY("transaction_id"),
	CONSTRAINT "creditcard_id" FOREIGN KEY("creditcard_id") REFERENCES "credit_card"("creditcard_id"),
	CONSTRAINT "doctor_id" FOREIGN KEY("doctor_id") REFERENCES "doctors"("doctor_id"),
	CONSTRAINT "customer_id" FOREIGN KEY("patient_id") REFERENCES "patients"("patient_id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER NOT NULL,
	"email"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"phone_number"	TEXT NOT NULL,
	"role"	TEXT NOT NULL,
	"created_at"	TIMESTAMP NOT NULL,
	CONSTRAINT "users_pk" PRIMARY KEY("user_id")
);
COMMIT;
