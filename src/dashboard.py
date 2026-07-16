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

# Define the SQL query for Chart 3: Top Hiring Companies
sql_top_companies = """
    SELECT 
        c.name AS company_name,
        COUNT(CASE WHEN o.accepted = TRUE THEN 1 END) AS offers_accepted
    FROM companies c
    JOIN offers o ON c.company_id = o.company_id
    GROUP BY c.company_id, c.name
    ORDER BY offers_accepted DESC
    LIMIT 5;
"""

# Define the SQL query for Chart 4: Applied vs Placed Gap
# We count how many unique students applied, and how many accepted an offer, grouped by department
sql_gap = """
    SELECT 
        s.department,
        COUNT(DISTINCT a.student_id) AS students_who_applied,
        COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN o.student_id END) AS students_placed
    FROM students s
    LEFT JOIN applications a ON s.student_id = a.student_id
    LEFT JOIN offers o ON s.student_id = o.student_id AND o.accepted = TRUE
    GROUP BY s.department
    ORDER BY students_who_applied DESC;
"""

# Use pandas to run the SQL queries and load the results into DataFrames (tables)
df_placement_rate = pd.read_sql_query(sql_placement_rate, conn)
df_package_trend = pd.read_sql_query(sql_package_trend, conn)
df_top_companies = pd.read_sql_query(sql_top_companies, conn)
df_gap = pd.read_sql_query(sql_gap, conn)

# Plotly puts the first row of data at the bottom for horizontal charts.
# We reverse our table (using .iloc[::-1]) to make the #1 company appear at the top!
df_top_companies = df_top_companies.iloc[::-1]

# Close the database connection safely since we already have all our data
conn.close()

# --- STEP 2: CREATE THE CHARTS ---
# Chart 1: Create a bar chart for placement rate
fig_placement_rate = px.bar(
    df_placement_rate,               
    x='department',                  
    y='placement_rate_percent',      
    title='Placement Rate by Department (%)' 
)

# Chart 2: Create a line chart for the average package trend over time
fig_package_trend = px.line(
    df_package_trend,                
    x='graduation_year',             
    y='avg_package_lpa',             
    color='department',              
    title='Average Package Trend Over Time (LPA)' 
)

# Chart 3: Create a horizontal bar chart for the top 5 hiring companies
fig_top_companies = px.bar(
    df_top_companies,                
    x='offers_accepted',             
    y='company_name',                
    orientation='h',                 
    title='Top 5 Hiring Companies (By Accepted Offers)' 
)

# Chart 4: Create a grouped bar chart for the applied vs placed gap
fig_gap = px.bar(
    df_gap,                                          # The new data table for the gap analysis
    x='department',                                  # Department on the bottom axis
    y=['students_who_applied', 'students_placed'],   # Plot BOTH of these columns on the vertical axis!
    barmode='group',                                 # Put the bars side-by-side (grouped) instead of stacking them on top of each other
    title='Applied vs Placed Gap by Department'      # Chart title
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
        
        # Add our second chart (Average Package Line Chart)
        dcc.Graph(
            id='package-trend-line-chart', 
            figure=fig_package_trend       
        ),
        
        # Add our third chart (Top Hiring Companies Horizontal Bar Chart)
        dcc.Graph(
            id='top-companies-bar-chart', 
            figure=fig_top_companies      
        ),
        
        # Add our fourth chart (Applied vs Placed Gap Grouped Bar Chart)
        dcc.Graph(
            id='applied-vs-placed-gap-chart', # A unique identifier for this new graph
            figure=fig_gap                    # We pass our new grouped bar chart to be displayed
        )
    ]
)

# Start the local development web server if we run this file directly
if __name__ == '__main__':
    app.run(debug=True)
