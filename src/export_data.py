# Import the database connection utility we built
from database import get_connection

# Import pandas to convert SQL query results into CSV files
import pandas as pd

# Import os to ensure the data directory exists
import os

# Import warnings to silence pandas connection warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

def export_tables_to_csv():
    # 1. Establish database connection
    conn = get_connection()
    
    # Ensure the data/ directory exists
    os.makedirs('data', exist_ok=True)
    
    # 2. Define the list of tables we want to export
    tables = ['students', 'companies', 'applications', 'offers']
    
    # 3. Loop through each table, fetch the data, and save it as a CSV file
    for table in tables:
        print(f"Exporting table '{table}' from ShaktiDB...")
        
        # Build SQL query to select everything from the current table
        query = f"SELECT * FROM {table};"
        
        # pd.read_sql_query reads all table rows into a pandas DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Define the target filepath inside the data/ folder
        csv_filepath = f"data/{table}.csv"
        
        # Save the DataFrame to a CSV file. 
        # index=False ensures pandas doesn't add an extra unnamed index column at the start.
        df.to_csv(csv_filepath, index=False)
        
        print(f"✅ Successfully saved: {csv_filepath} ({len(df)} rows)")
        
    # 4. Close the database connection
    conn.close()
    print("🎉 All tables successfully exported for Power BI!")

if __name__ == "__main__":
    print("Starting data export process...")
    export_tables_to_csv()
