# Import the connection function we built in the last step
from database import get_connection

# Function to create our four database tables
def create_tables():
    # 1. Get the connection (pick up the phone to the database)
    conn = get_connection()
    
    # 2. Create a 'cursor'. A cursor is like a pen that writes SQL commands to the database.
    cursor = conn.cursor()
    
    # 3. Write and execute the SQL to create the 'students' table
    # SERIAL means the ID will auto-increase (1, 2, 3...). 
    # VARCHAR is text. NUMERIC(4,2) means a number with up to 2 decimal places (like 9.55).
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        department VARCHAR(50) NOT NULL,
        cgpa NUMERIC(4,2) NOT NULL,
        graduation_year INTEGER NOT NULL
    );
    """)
    
    # 4. Write and execute the SQL to create the 'companies' table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        company_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        industry VARCHAR(50) NOT NULL
    );
    """)
    
    # 5. Write and execute the SQL to create the 'applications' table
    # 'REFERENCES' creates a link (Foreign Key) to the students and companies tables.
    # This ensures an application can only belong to a real student and real company.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        application_id SERIAL PRIMARY KEY,
        student_id INTEGER REFERENCES students(student_id),
        company_id INTEGER REFERENCES companies(company_id),
        status VARCHAR(20) NOT NULL
    );
    """)
    
    # 6. Write and execute the SQL to create the 'offers' table
    # BOOLEAN stores True (Accepted) or False (Rejected)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offers (
        offer_id SERIAL PRIMARY KEY,
        application_id INTEGER REFERENCES applications(application_id),
        student_id INTEGER REFERENCES students(student_id),
        company_id INTEGER REFERENCES companies(company_id),
        package_lpa NUMERIC(5,2) NOT NULL,
        accepted BOOLEAN NOT NULL
    );
    """)
    
    # 7. VERY IMPORTANT: Commit the changes. 
    # If we don't commit, it's like typing a Word document and closing it without hitting Save.
    conn.commit()
    
    # Print success message
    print("✅ All four tables (students, companies, applications, offers) created successfully!")
    
    # 8. Close the pen and hang up the phone
    cursor.close()
    conn.close()

# Check if we are running this file directly
if __name__ == "__main__":
    print("Creating tables in ShaktiDB...")
    create_tables()
