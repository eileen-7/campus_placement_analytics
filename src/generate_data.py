# Import the database connection utility we built
from database import get_connection

# Import Faker for generating realistic names
from faker import Faker

# Import random for generating numbers and making decisions
import random

# Initialize Faker with Indian locale to generate realistic Indian names
fake = Faker('en_IN')

# Set a random seed so that every time we run this, we get the exact same data
random.seed(42)
Faker.seed(42)

def generate_sample_data():
    # 1. Establish database connection
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Clearing existing data from tables...")
    # TRUNCATE removes all rows, RESTART IDENTITY resets serial auto-increments to 1, CASCADE handles foreign key constraints
    cursor.execute("TRUNCATE TABLE offers, applications, companies, students RESTART IDENTITY CASCADE;")
    
    # 2. Define realistic companies
    companies_data = [
        ("Google", "Software"),
        ("Microsoft", "Software"),
        ("Tata Consultancy Services", "Software"),
        ("Infosys", "Software"),
        ("Goldman Sachs", "Finance"),
        ("JPMorgan Chase", "Finance"),
        ("McKinsey & Company", "Consulting"),
        ("Boston Consulting Group", "Consulting"),
        ("Larsen & Toubro", "Core Engineering"),
        ("Reliance Industries", "Core Engineering"),
        ("Intel", "Software"),
        ("HDFC Bank", "Finance"),
        ("Cognizant", "Software"),
        ("Tata Motors", "Core Engineering"),
        ("Bain & Company", "Consulting")
    ]
    
    print("Inserting companies...")
    inserted_companies = []
    for name, industry in companies_data:
        cursor.execute(
            "INSERT INTO companies (name, industry) VALUES (%s, %s) RETURNING company_id;",
            (name, industry)
        )
        company_id = cursor.fetchone()[0]
        inserted_companies.append((company_id, name, industry))
        
    # 3. Generate 200 Students
    departments = [
        "Computer Science",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Chemical Engineering"
    ]
    
    print("Inserting 200 students...")
    students = []
    for _ in range(200):
        name = fake.name()
        department = random.choice(departments)
        # Generate CGPA following a realistic distribution (between 6.0 and 10.0)
        cgpa = round(random.uniform(6.5, 9.8), 2)
        # Generate students across multiple years so we can see a trend over time
        graduation_year = random.choice([2023, 2024, 2025, 2026])
        
        cursor.execute(
            "INSERT INTO students (name, department, cgpa, graduation_year) VALUES (%s, %s, %s, %s) RETURNING student_id;",
            (name, department, cgpa, graduation_year)
        )
        student_id = cursor.fetchone()[0]
        students.append({
            "id": student_id,
            "name": name,
            "department": department,
            "cgpa": cgpa
        })
        
    # 4. Generate Applications & Offers
    print("Generating applications and offers...")
    
    # We will track offers student-by-student to ensure realistic acceptance behavior
    for student in students:
        student_id = student["id"]
        cgpa = student["cgpa"]
        dept = student["department"]
        
        # Decide how many companies a student applies to (between 2 and 5)
        num_applications = random.randint(2, 5)
        # Select random companies for this student to apply to
        applied_companies = random.sample(inserted_companies, num_applications)
        
        # Store offers received by this specific student: list of dictionaries
        student_offers = []
        
        for company_id, comp_name, industry in applied_companies:
            # Determine selection probability based on student's CGPA
            if cgpa >= 9.0:
                probability = 0.65
            elif cgpa >= 8.0:
                probability = 0.45
            elif cgpa >= 7.0:
                probability = 0.20
            else:
                probability = 0.05
                
            # Roll a random number to decide application outcome
            roll = random.random()
            if roll < probability:
                status = "Selected"
            elif roll < (probability + 0.15):
                status = "Applied"  # Still in progress
            else:
                status = "Rejected"
                
            # Insert application record
            cursor.execute(
                "INSERT INTO applications (student_id, company_id, status) VALUES (%s, %s, %s) RETURNING application_id;",
                (student_id, company_id, status)
            )
            application_id = cursor.fetchone()[0]
            
            # If the student was Selected, they receive a job offer
            if status == "Selected":
                # Calculate salary package LPA based on industry and CGPA
                if dept == "Computer Science" or industry == "Software":
                    base = random.uniform(12.0, 22.0)
                    bonus = (cgpa - 7.5) * 4.0
                elif industry == "Finance":
                    base = random.uniform(10.0, 18.0)
                    bonus = (cgpa - 7.5) * 3.0
                elif industry == "Consulting":
                    base = random.uniform(8.0, 15.0)
                    bonus = (cgpa - 7.5) * 2.0
                else:  # Core Engineering / Other
                    base = random.uniform(6.0, 11.0)
                    bonus = (cgpa - 7.5) * 1.5
                    
                package = round(base + bonus, 2)
                # Keep packages in a realistic boundary (minimum 4.5 LPA, maximum 45.0 LPA)
                package = max(4.5, min(package, 45.0))
                
                student_offers.append({
                    "application_id": application_id,
                    "company_id": company_id,
                    "package_lpa": package
                })
                
        # If the student has offers, handle which one they accept
        if student_offers:
            # Sort offers by package in descending order so the highest package is first
            student_offers.sort(key=lambda x: x["package_lpa"], reverse=True)
            
            # Student accepts the highest package with 90% probability
            # (10% probability they reject all, e.g., for higher studies or off-campus opportunities)
            accepts_any = random.random() < 0.90
            
            for index, offer in enumerate(student_offers):
                # The first item (index 0) is the highest offer
                accepted = (index == 0) and accepts_any
                
                # Insert offer record
                cursor.execute(
                    """
                    INSERT INTO offers (application_id, student_id, company_id, package_lpa, accepted)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (offer["application_id"], student_id, offer["company_id"], offer["package_lpa"], accepted)
                )
                
    # Commit all changes to ShaktiDB
    conn.commit()
    print("✅ Sample data generation completed successfully!")
    
    # Close resources
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("Starting sample data generation for ShaktiDB...")
    generate_sample_data()
