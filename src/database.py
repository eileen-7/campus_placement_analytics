# Import the psycopg2 library, which acts as the translator between Python and ShaktiDB
import psycopg2

# Import the sys library, which allows us to stop the program if an error happens
import sys

# Define a reusable function that creates and returns a database connection
def get_connection():
    try:
        # Attempt to connect to the database using the provided credentials
        # NOTE: You MUST change 'user' and 'password' to match your actual ShaktiDB setup!
        conn = psycopg2.connect(
            host="localhost",    # 'localhost' means the database is on this same computer
            database="postgres", # The default database name created when installing
            user="postgres",     # The default superuser account
            password="eileen"  # REPLACE THIS with your actual database password
        )
        
        # If the connection succeeds, return the connection object for other files to use
        return conn
        
    # If anything goes wrong during connection, catch the error so we can handle it cleanly
    except Exception as error:
        # Print a red cross and the exact error message so we know what to fix
        print(f"❌ Database connection failed: {error}")
        
        # Stop the Python program entirely because we can't continue without a database
        sys.exit(1)

# This special condition checks if we are running this specific file directly from the terminal
if __name__ == "__main__":
    # Tell the user what we are currently trying to do
    print("Testing connection to ShaktiDB...")
    
    # Call our function to attempt the connection
    test_conn = get_connection()
    
    # If we made it to this line, the connection did not crash and was successful!
    print("✅ Connection successful! Python is talking to ShaktiDB.")
    
    # It is good practice to politely close the connection when we are done using it
    test_conn.close()
