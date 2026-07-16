# Import the main Dash class to create our web application
from dash import Dash
# Import html components to create standard web elements like headings
from dash import html
# Import dcc (Dash Core Components) which includes the Graph component for displaying charts
from dash import dcc
# Import Plotly Express to easily draw our charts
import plotly.express as px
# Import pandas to handle our database results as a table
import pandas as pd
# Import our custom database connection function from database.py
from database import get_connection
# Import warnings to hide a harmless warning pandas throws when connecting directly to the database
import warnings

# Tell Python to ignore harmless UserWarnings from pandas
warnings.filterwarnings('ignore', category=UserWarning)

# Initialize the Dash application
app = Dash(__name__)

# --- STEP 1: FETCH DATA FROM SHAKTIDB ---
# Connect to the database
conn = get_connection()

# Define the SQL query to calculate the placement rate percentage for each department
sql_query = """
    SELECT 
        s.department,
        ROUND(
            (COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN s.student_id END)::NUMERIC / COUNT(DISTINCT s.student_id) * 100), 
            2
        ) AS placement_rate_percent
    FROM students s
    LEFT JOIN offers o ON s.student_id = o.student_id
    GROUP BY s.department
    ORDER BY placement_rate_percent DESC;
"""

# Use pandas to run the SQL query and load the results into a DataFrame (a data table)
df_placement_rate = pd.read_sql_query(sql_query, conn)

# Close the database connection safely since we already have the data
conn.close()

# --- STEP 2: CREATE THE CHART ---
# Create a bar chart using Plotly Express
fig_placement_rate = px.bar(
    df_placement_rate,               # The data table we just created
    x='department',                  # The column to use for the bottom axis (horizontal)
    y='placement_rate_percent',      # The column to use for the height of the bars (vertical)
    title='Placement Rate by Department (%)' # The title displayed above the chart
)

# --- STEP 3: DASHBOARD LAYOUT ---
# Define what the user will see on the screen
app.layout = html.Div(
    children=[
        # Main heading for the dashboard
        html.H1(children='Campus Placement Analytics Dashboard'),
        
        # Add the chart to our webpage layout using the dcc.Graph component
        dcc.Graph(
            id='placement-rate-bar-chart', # A unique identifier for this specific graph
            figure=fig_placement_rate      # We pass our created chart figure to be displayed
        )
    ]
)

# Start the local development web server if we run this file directly
if __name__ == '__main__':
    app.run(debug=True)

