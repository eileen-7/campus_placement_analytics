# Import the main Dash class to create our web application
from dash import Dash
# Import html components to create standard web elements like headings
from dash import html
# Import dcc (Dash Core Components) for interactive widgets like Dropdowns and Graphs
from dash import dcc
# Import Input and Output to connect our dropdowns to our charts
from dash import Input, Output
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

# --- STEP 1: GET DROPDOWN OPTIONS ON STARTUP ---
# We need to know what years and departments actually exist in the database 
# so we can put them in our dropdown menus.
conn = get_connection()
# Ask the database for all the unique years and unique departments
df_years = pd.read_sql_query("SELECT DISTINCT graduation_year FROM students ORDER BY graduation_year;", conn)
df_depts = pd.read_sql_query("SELECT DISTINCT department FROM students ORDER BY department;", conn)
conn.close()

# Convert those results into simple Python lists
available_years = df_years['graduation_year'].tolist()
available_departments = df_depts['department'].tolist()


# --- STEP 2: DASHBOARD LAYOUT ---
# Define what the user will see on the screen
app.layout = html.Div(
    children=[
        # Main heading for the dashboard
        html.H1(children='Campus Placement Analytics Dashboard'),
        
        # Add our Interactive Filters! 
        html.Div(
            children=[
                html.Label('Filter by Graduation Year:'),
                dcc.Dropdown(
                    id='year-filter', # Unique ID we will use to listen for changes
                    # Create an option for every year, plus an "All" option
                    options=[{'label': 'All Years', 'value': 'All'}] + [{'label': str(y), 'value': y} for y in available_years],
                    value='All' # The default selected value
                ),
                
                html.Label('Filter by Department:'),
                dcc.Dropdown(
                    id='department-filter', # Unique ID we will use to listen for changes
                    # Create an option for every department, plus an "All" option
                    options=[{'label': 'All Departments', 'value': 'All'}] + [{'label': d, 'value': d} for d in available_departments],
                    value='All' # The default selected value
                )
            ], 
            style={'width': '50%', 'marginBottom': '30px'} # Add a little spacing and width limit
        ),
        
        # Add our four chart placeholders (They start empty and get filled by the callback!)
        dcc.Graph(id='placement-rate-bar-chart'),
        dcc.Graph(id='package-trend-line-chart'),
        dcc.Graph(id='top-companies-bar-chart'),
        dcc.Graph(id='applied-vs-placed-gap-chart')
    ]
)

# --- STEP 3: THE INTERACTIVE CALLBACK ---
# The @app.callback is the "brain" of the interactive dashboard. 
# It listens to the Inputs (our dropdowns) and updates the Outputs (our graphs).
@app.callback(
    [Output('placement-rate-bar-chart', 'figure'),
     Output('package-trend-line-chart', 'figure'),
     Output('top-companies-bar-chart', 'figure'),
     Output('applied-vs-placed-gap-chart', 'figure')],
    [Input('year-filter', 'value'),
     Input('department-filter', 'value')]
)
def update_charts(selected_year, selected_dept):
    # Every time a user changes a dropdown, this function runs!
    
    # Re-connect to the database to fetch fresh, filtered data
    conn = get_connection()
    
    # 1. Build our SQL Filters based on what the user selected
    # If they selected "All", we use "1=1" which is a database trick that means "no filter".
    year_filter = f"s.graduation_year = {selected_year}" if selected_year != 'All' else "1=1"
    dept_filter = f"s.department = '{selected_dept}'" if selected_dept != 'All' else "1=1"
    
    # Combine the filters. Example result: "s.graduation_year = 2023 AND s.department = 'Computer Science'"
    filters = f"{year_filter} AND {dept_filter}"
    
    # 2. Write the 4 SQL Queries, injecting our dynamic filters into the WHERE clause
    sql_placement = f"""
        SELECT 
            s.department,
            ROUND(
                (COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN s.student_id END)::NUMERIC / COUNT(DISTINCT s.student_id) * 100), 
                2
            ) AS placement_rate_percent
        FROM students s
        LEFT JOIN offers o ON s.student_id = o.student_id
        WHERE {filters}
        GROUP BY s.department
        ORDER BY placement_rate_percent DESC;
    """
    
    sql_trend = f"""
        SELECT 
            s.graduation_year,
            s.department,
            ROUND(AVG(o.package_lpa), 2) AS avg_package_lpa
        FROM students s
        JOIN offers o ON s.student_id = o.student_id
        WHERE o.accepted = TRUE AND {filters}
        GROUP BY s.graduation_year, s.department
        ORDER BY s.graduation_year, s.department;
    """
    
    sql_top_companies = f"""
        SELECT 
            c.name AS company_name,
            COUNT(CASE WHEN o.accepted = TRUE THEN 1 END) AS offers_accepted
        FROM companies c
        JOIN offers o ON c.company_id = o.company_id
        JOIN students s ON o.student_id = s.student_id
        WHERE {filters}
        GROUP BY c.company_id, c.name
        ORDER BY offers_accepted DESC
        LIMIT 5;
    """
    
    sql_gap = f"""
        SELECT 
            s.department,
            COUNT(DISTINCT a.student_id) AS students_who_applied,
            COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN o.student_id END) AS students_placed
        FROM students s
        LEFT JOIN applications a ON s.student_id = a.student_id
        LEFT JOIN offers o ON s.student_id = o.student_id AND o.accepted = TRUE
        WHERE {filters}
        GROUP BY s.department
        ORDER BY students_who_applied DESC;
    """
    
    # 3. Run the queries
    df_placement = pd.read_sql_query(sql_placement, conn)
    df_trend = pd.read_sql_query(sql_trend, conn)
    df_top_companies = pd.read_sql_query(sql_top_companies, conn)
    df_gap = pd.read_sql_query(sql_gap, conn)
    
    # Reverse top companies so the #1 company is at the top of the horizontal chart
    df_top_companies = df_top_companies.iloc[::-1]
    
    # Close connection
    conn.close()
    
    # 4. Create the chart figures from the newly filtered data
    fig1 = px.bar(df_placement, x='department', y='placement_rate_percent', title='Placement Rate by Department (%)')
    fig2 = px.line(df_trend, x='graduation_year', y='avg_package_lpa', color='department', title='Average Package Trend Over Time (LPA)')
    fig3 = px.bar(df_top_companies, x='offers_accepted', y='company_name', orientation='h', title='Top 5 Hiring Companies (By Accepted Offers)')
    fig4 = px.bar(df_gap, x='department', y=['students_who_applied', 'students_placed'], barmode='group', title='Applied vs Placed Gap by Department')
    
    # Return the four figures in the exact order we defined them in the Output list above
    return fig1, fig2, fig3, fig4

# Start the local development web server if we run this file directly
if __name__ == '__main__':
    app.run(debug=True)

