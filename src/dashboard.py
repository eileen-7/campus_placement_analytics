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

# Define the SQL query for Chart 1: Placement Rate by Department
sql_placement_rate = """
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

# Define the SQL query for Chart 2: Average Package Trend
# We want to see how the average package changes over the graduation years for each department
sql_package_trend = """
    SELECT 
        s.graduation_year,
        s.department,
        ROUND(AVG(o.package_lpa), 2) AS avg_package_lpa
    FROM students s
    JOIN offers o ON s.student_id = o.student_id
    WHERE o.accepted = TRUE
    GROUP BY s.graduation_year, s.department
    ORDER BY s.graduation_year, s.department;
"""

# Use pandas to run the SQL queries and load the results into DataFrames (tables)
df_placement_rate = pd.read_sql_query(sql_placement_rate, conn)
df_package_trend = pd.read_sql_query(sql_package_trend, conn)

# Close the database connection safely since we already have all our data
conn.close()

# --- STEP 2: CREATE THE CHARTS ---
# Chart 1: Create a bar chart for placement rate
fig_placement_rate = px.bar(
    df_placement_rate,               # The first data table
    x='department',                  # Bottom axis
    y='placement_rate_percent',      # Vertical axis
    title='Placement Rate by Department (%)' # Chart title
)

# Chart 2: Create a line chart for the average package trend over time
fig_package_trend = px.line(
    df_package_trend,                # The new data table for salary trends
    x='graduation_year',             # Time (years) on the bottom axis
    y='avg_package_lpa',             # Salary package on the vertical axis
    color='department',              # Draw a separate colored line for each department
    title='Average Package Trend Over Time (LPA)' # Chart title
)

# --- STEP 3: DASHBOARD LAYOUT ---
# Define what the user will see on the screen
app.layout = html.Div(
    children=[
        # Main heading for the dashboard
        html.H1(children='Campus Placement Analytics Dashboard'),
        
        # Add our first chart (Placement Rate Bar Chart)
        dcc.Graph(
            id='placement-rate-bar-chart',
            figure=fig_placement_rate
        ),
        
        # Add our second chart (Average Package Line Chart) right below the first one
        dcc.Graph(
            id='package-trend-line-chart', # A unique identifier for this new graph
            figure=fig_package_trend       # We pass our new line chart figure to be displayed
        )
    ]
)

# Start the local development web server if we run this file directly
if __name__ == '__main__':
    app.run(debug=True)
