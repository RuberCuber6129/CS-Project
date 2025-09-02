import mysql.connector as mysql


DB_CONFIG = {
    "host": "localhost",
    "user": "root",        # change if different
    "password": "root"     # change if different
}


try:
    # Connect to MySQL server
    conn = mysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS clinicDB")

    # Select the database
    cursor.execute("USE clinicDB")

    # Create student_school table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_school (
            std_id INT PRIMARY KEY,
            class INT,
            section VARCHAR(2),
            gender VARCHAR(6),
            join_date DATE
        )
    """)

    # Create student_contact table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_contact (
            std_id INT,
            phone_number VARCHAR(15),
            email_address VARCHAR(100),
            emergency_contact_name VARCHAR(100),
            emergency_contact_phone VARCHAR(15),
            relationship VARCHAR(50),
            address TEXT,
            PRIMARY KEY(std_id),
            FOREIGN KEY(std_id) REFERENCES student_school(std_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)

    # ==========================
    # Insert Sample Data
    # ==========================
    students = [
        (1, 10, 'A', 'Male', '2022-06-15'),
        (2, 11, 'B', 'Female', '2021-07-20'),
        (3, 9,  'C', 'Male', '2023-01-10'),
        (4, 12, 'A', 'Female', '2020-09-05')
    ]

    contacts = [
        (1, '0501234567', 'john.doe@email.com', 'Mary Doe', '0507654321', 'Mother', '123 Palm St, Abu Dhabi'),
        (2, '0502345678', 'sara.smith@email.com', 'David Smith', '0508765432', 'Father', '45 Marina Rd, Dubai'),
        (3, '0503456789', 'ali.khan@email.com', 'Aisha Khan', '0509876543', 'Sister', '78 Desert Ln, Sharjah'),
        (4, '0504567890', 'fatima.ali@email.com', 'Omar Ali', '0506543210', 'Brother', '12 Corniche Ave, Al Ain')
    ]

    cursor.executemany("""
        INSERT IGNORE INTO student_school (std_id, class, section, gender, join_date)
        VALUES (%s, %s, %s, %s, %s)
    """, students)

    cursor.executemany("""
        INSERT IGNORE INTO student_contact (std_id, phone_number, email_address, emergency_contact_name,
                                            emergency_contact_phone, relationship, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, contacts)

    conn.commit()

    print("✅ Database, tables, and sample data created successfully.")

except mysql.Error as e:
    print(f"❌ Error: {e}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
