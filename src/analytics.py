# Import the database connection utility we built
from database import get_connection

# Import pandas to display query results in clean, formatted tables
import pandas as pd

# Import warnings to ignore harmless psycopg2 connection warnings from pandas
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

def run_analytics():
    # 1. Establish database connection
    conn = get_connection()
    
    # 2. Define our 4 analytical queries
    queries = {
        "1. Placement Rate by Department": """
            SELECT 
                s.department,
                COUNT(DISTINCT s.student_id) AS total_students,
                COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN s.student_id END) AS placed_students,
                ROUND(
                    (COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN s.student_id END)::NUMERIC / COUNT(DISTINCT s.student_id) * 100), 
                    2
                ) AS placement_rate_percent
            FROM students s
            LEFT JOIN offers o ON s.student_id = o.student_id
            GROUP BY s.department
            ORDER BY placement_rate_percent DESC;
        """,
        
        "2. Average Package (Salary) Trends by Department (Accepted Offers)": """
            SELECT 
                s.department,
                ROUND(AVG(o.package_lpa), 2) AS avg_package_lpa,
                MAX(o.package_lpa) AS max_package_lpa,
                MIN(o.package_lpa) AS min_package_lpa
            FROM students s
            JOIN offers o ON s.student_id = o.student_id
            WHERE o.accepted = TRUE
            GROUP BY s.department
            ORDER BY avg_package_lpa DESC;
        """,
        
        "3. Top 5 Hiring Companies (By Accepted Offers)": """
            SELECT 
                c.name AS company_name,
                c.industry,
                COUNT(o.offer_id) AS total_offers_made,
                COUNT(CASE WHEN o.accepted = TRUE THEN 1 END) AS offers_accepted
            FROM companies c
            JOIN offers o ON c.company_id = o.company_id
            GROUP BY c.company_id, c.name, c.industry
            ORDER BY offers_accepted DESC, total_offers_made DESC
            LIMIT 5;
        """,
        
        "4. Applied vs. Placed Gap (Student Funnel Analysis)": """
            SELECT 
                s.department,
                COUNT(DISTINCT s.student_id) AS total_students,
                COUNT(DISTINCT a.student_id) AS students_who_applied,
                COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN o.student_id END) AS students_placed,
                COUNT(DISTINCT s.student_id) - COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN o.student_id END) AS gap_unplaced
            FROM students s
            LEFT JOIN applications a ON s.student_id = a.student_id
            LEFT JOIN offers o ON s.student_id = o.student_id AND o.accepted = TRUE
            GROUP BY s.department
            ORDER BY total_students DESC;
        """
    }
    
    # 3. Loop through and execute each query
    for title, sql_query in queries.items():
        print("\n" + "="*60)
        print(f" ANALYTICS REPORT: {title}")
        print("="*60)
        
        # pd.read_sql_query executes the SQL and loads the result directly into a pandas DataFrame table
        df = pd.read_sql_query(sql_query, conn)
        
        # Display the DataFrame in a clean tabular view
        print(df.to_string(index=False))
        print("="*60 + "\n")
        
    # 4. Close the database connection
    conn.close()

if __name__ == "__main__":
    print("Running Campus Placement Analytics Queries in ShaktiDB...")
    run_analytics()
