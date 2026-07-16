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

# Initialize the Dash application with a clean default font
app = Dash(__name__)

# --- STEP 1: GET DROPDOWN OPTIONS ON STARTUP ---
conn = get_connection()
df_years = pd.read_sql_query("SELECT DISTINCT graduation_year FROM students ORDER BY graduation_year;", conn)
df_depts = pd.read_sql_query("SELECT DISTINCT department FROM students ORDER BY department;", conn)
conn.close()

available_years = df_years['graduation_year'].tolist()
available_departments = df_depts['department'].tolist()

# --- CSS STYLES ---
# We define some Python dictionaries containing CSS styles to make our dashboard look professional
PAGE_STYLE = {
    'backgroundColor': '#F4F7FC', # A very light, clean greyish-blue background
    'padding': '40px', 
    'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif'
}

CARD_STYLE = {
    'backgroundColor': 'white', 
    'padding': '20px', 
    'borderRadius': '12px', 
    'boxShadow': '0 4px 8px rgba(0,0,0,0.05)', # Subtle shadow for a "floating" card effect
    'flex': 1
}

FILTER_CONTAINER_STYLE = {
    'backgroundColor': 'white', 
    'padding': '20px', 
    'borderRadius': '12px', 
    'boxShadow': '0 4px 8px rgba(0,0,0,0.05)',
    'marginBottom': '30px',
    'display': 'flex', 
    'gap': '30px' # Space between the two dropdowns
}

ROW_STYLE = {
    'display': 'flex', 
    'gap': '30px', 
    'marginBottom': '30px'
}

# --- STEP 2: DASHBOARD LAYOUT ---
app.layout = html.Div(
    style=PAGE_STYLE,
    children=[
        # Main heading with an emoji
        html.H1(
            children='🎓 Campus Placement Analytics',
            style={'textAlign': 'center', 'color': '#2C3E50', 'marginBottom': '40px', 'fontWeight': 'bold'}
        ),
        
        # Interactive Filters Container
        html.Div(
            style=FILTER_CONTAINER_STYLE,
            children=[
                html.Div([
                    html.Label('Graduation Year:', style={'fontWeight': 'bold', 'color': '#34495E', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': 'All Years', 'value': 'All'}] + [{'label': str(y), 'value': y} for y in available_years],
                        value='All',
                        clearable=False
                    )
                ], style={'flex': 1}),
                
                html.Div([
                    html.Label('Department:', style={'fontWeight': 'bold', 'color': '#34495E', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='department-filter',
                        options=[{'label': 'All Departments', 'value': 'All'}] + [{'label': d, 'value': d} for d in available_departments],
                        value='All',
                        clearable=False
                    )
                ], style={'flex': 1})
            ]
        ),
        
        # Charts Grid - Row 1
        html.Div(
            style=ROW_STYLE,
            children=[
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id='placement-rate-bar-chart')]),
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id='package-trend-line-chart')])
            ]
        ),
        
        # Charts Grid - Row 2
        html.Div(
            style=ROW_STYLE,
            children=[
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id='top-companies-bar-chart')]),
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id='applied-vs-placed-gap-chart')])
            ]
        )
    ]
)

# --- STEP 3: THE INTERACTIVE CALLBACK ---
@app.callback(
    [Output('placement-rate-bar-chart', 'figure'),
     Output('package-trend-line-chart', 'figure'),
     Output('top-companies-bar-chart', 'figure'),
     Output('applied-vs-placed-gap-chart', 'figure')],
    [Input('year-filter', 'value'),
     Input('department-filter', 'value')]
)
def update_charts(selected_year, selected_dept):
    conn = get_connection()
    
    # 1. Build SQL Filters
    year_filter = f"s.graduation_year = {selected_year}" if selected_year != 'All' else "1=1"
    dept_filter = f"s.department = '{selected_dept}'" if selected_dept != 'All' else "1=1"
    filters = f"{year_filter} AND {dept_filter}"
    
    # 2. Write the 4 SQL Queries
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
    df_top_companies = df_top_companies.iloc[::-1]
    conn.close()
    
    # 4. Create the chart figures with a clean 'plotly_white' template and consistent colors
    CHART_TEMPLATE = 'plotly_white'
    MAIN_COLOR = '#3498DB' # Professional Dash Blue
    
    fig1 = px.bar(
        df_placement, x='department', y='placement_rate_percent', 
        title='Placement Rate by Department (%)',
        template=CHART_TEMPLATE, color_discrete_sequence=[MAIN_COLOR]
    )
    
    fig2 = px.line(
        df_trend, x='graduation_year', y='avg_package_lpa', color='department', 
        title='Average Package Trend Over Time (LPA)',
        template=CHART_TEMPLATE, color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    fig3 = px.bar(
        df_top_companies, x='offers_accepted', y='company_name', orientation='h', 
        title='Top 5 Hiring Companies (By Accepted Offers)',
        template=CHART_TEMPLATE, color_discrete_sequence=[MAIN_COLOR]
    )
    
    fig4 = px.bar(
        df_gap, x='department', y=['students_who_applied', 'students_placed'], barmode='group', 
        title='Applied vs Placed Gap by Department',
        template=CHART_TEMPLATE, color_discrete_sequence=['#95A5A6', '#2ECC71'] # Grey for applied, Green for placed
    )
    
    # Remove the transparent background of the graphs to blend with the white cards
    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    return fig1, fig2, fig3, fig4

# Start the local development web server
if __name__ == '__main__':
    app.run(debug=True)
