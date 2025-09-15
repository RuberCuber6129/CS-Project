import mysql.connector as mysql

def run():
    conn = None
    try:
        # ✅ Connect to MySQL (make sure clinicDB exists)
        conn = mysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="clinicDB"
        )
        cur = conn.cursor()

        # --- Existing demo tables (kept if already present) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS student_school (
                std_id INT PRIMARY KEY,
                class INT,
                section VARCHAR(10),
                gender VARCHAR(10),
                join_date DATE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS student_contact (
                std_id INT PRIMARY KEY,
                phone_number VARCHAR(20),
                email_address VARCHAR(100),
                emergency_contact_name VARCHAR(100),
                emergency_contact_phone VARCHAR(20),
                relationship VARCHAR(50),
                address VARCHAR(200),
                FOREIGN KEY(std_id) REFERENCES student_school(std_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        # Seed sample data if empty (idempotent)
        cur.execute("SELECT COUNT(*) FROM student_school")
        if cur.fetchone()[0] == 0:
            students = [
                (1, 10, 'A', 'Male',   '2022-06-15'),
                (2, 11, 'B', 'Female', '2021-07-20'),
                (3, 9,  'C', 'Male',   '2023-01-10'),
                (4, 12, 'A', 'Female', '2020-09-05'),
            ]
            cur.executemany("""
                INSERT IGNORE INTO student_school (std_id, class, section, gender, join_date)
                VALUES (%s, %s, %s, %s, %s)
            """, students)

        cur.execute("SELECT COUNT(*) FROM student_contact")
        if cur.fetchone()[0] == 0:
            contacts = [
                (1, '0501234567', 'john.doe@email.com',  'Mary Doe',  '0507654321', 'Mother', '123 Palm St, Abu Dhabi'),
                (2, '0502345678', 'sara.smith@email.com','David Smith','0508765432', 'Father', '45 Marina Rd, Dubai'),
                (3, '0503456789', 'ali.khan@email.com',  'Aisha Khan','0509876543', 'Sister', '78 Desert Ln, Sharjah'),
                (4, '0504567890', 'fatima.ali@email.com','Omar Ali',  '0506543210', 'Brother','12 Corniche Ave, Al Ain'),
            ]
            cur.executemany("""
                INSERT IGNORE INTO student_contact (std_id, phone_number, email_address, emergency_contact_name,
                                                    emergency_contact_phone, relationship, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, contacts)

        # --- Lookup table for statuses ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment_status (
                status_id INT PRIMARY KEY,
                status_name VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        cur.executemany("""
            INSERT IGNORE INTO appointment_status (status_id, status_name)
            VALUES (%s, %s)
        """, [
            (1, "Scheduled"),
            (2, "Completed"),
            (3, "Canceled"),
            (4, "No-Show"),
            (5, "Rescheduled"),
        ])

        # --- Permanent merged table ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS student_info (
                student_id INT PRIMARY KEY,
                name VARCHAR(100),
                class INT,
                section VARCHAR(10),
                gender VARCHAR(10),
                join_date DATE,
                phone_number VARCHAR(20),
                email_address VARCHAR(100),
                emergency_contact_name VARCHAR(100),
                emergency_contact_phone VARCHAR(20),
                relationship VARCHAR(50),
                address VARCHAR(200),
                medical_history TEXT,
                status_id INT,
                FOREIGN KEY(status_id) REFERENCES appointment_status(status_id)
                    ON UPDATE CASCADE
                    ON DELETE SET NULL
            )
        """)

        # ✅ Create indexes manually if they don’t exist
        cur.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE table_schema = 'clinicDB'
              AND table_name = 'student_info'
              AND index_name = 'idx_student_info_class'
        """)
        if cur.fetchone()[0] == 0:
            cur.execute("CREATE INDEX idx_student_info_class ON student_info(class)")

        cur.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE table_schema = 'clinicDB'
              AND table_name = 'student_info'
              AND index_name = 'idx_student_info_status'
        """)
        if cur.fetchone()[0] == 0:
            cur.execute("CREATE INDEX idx_student_info_status ON student_info(status_id)")

        # --- Migrate data ---
        cur.execute("""
            INSERT IGNORE INTO student_info (
                student_id, name, class, section, gender, join_date,
                phone_number, email_address, emergency_contact_name, emergency_contact_phone,
                relationship, address, medical_history, status_id
            )
            SELECT
                s.std_id AS student_id,
                NULL AS name,
                s.class,
                s.section,
                s.gender,
                s.join_date,
                c.phone_number,
                c.email_address,
                c.emergency_contact_name,
                c.emergency_contact_phone,
                c.relationship,
                c.address,
                NULL AS medical_history,
                NULL AS status_id
            FROM student_school s
            LEFT JOIN student_contact c ON c.std_id = s.std_id
        """)

        # --- Appointments table ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_name VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status_id INT NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES student_info(student_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE,
                FOREIGN KEY(status_id) REFERENCES appointment_status(status_id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            )
        """)

        # ✅ Index checks for appointments
        for idx_name, col in [
            ("idx_appointments_patient", "patient_id"),
            ("idx_appointments_status", "status_id"),
            ("idx_appointments_date", "date"),
        ]:
            cur.execute(f"""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE table_schema = 'clinicDB'
                  AND table_name = 'appointments'
                  AND index_name = '{idx_name}'
            """)
            if cur.fetchone()[0] == 0:
                cur.execute(f"CREATE INDEX {idx_name} ON appointments({col})")

        # Seed appointments
        cur.executemany("""
            INSERT IGNORE INTO appointments (appointment_id, patient_id, doctor_name, date, time, status_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [
            (1, 1, "Dr. Ahmed", "2025-09-10", "09:30:00", 1),
            (2, 2, "Dr. Lina",  "2025-09-11", "11:00:00", 2),
        ])

        conn.commit()
        print("✅ student_info created, statuses seeded, appointments table ready, and data migrated.")

    except mysql.Error as e:
        if conn:
            conn.rollback()
        print(f"❌ MySQL error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run()
