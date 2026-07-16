# Import the database connection utility we built
from database import get_connection

# Import matplotlib for plotting charts
import matplotlib.pyplot as plt

# Import pandas to easily fetch SQL results into tables
import pandas as pd

# Import os to ensure the charts directory exists
import os

# Import warnings to silence pandas warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

def generate_charts():
    # 1. Establish database connection
    conn = get_connection()
    
    # Ensure the charts/ directory exists
    os.makedirs('charts', exist_ok=True)
    
    # Set a clean professional style for our plots
    plt.style.use('ggplot')
    # Use clean modern fonts and customize colors
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['font.family'] = 'sans-serif'
    
    # -------------------------------------------------------------
    # CHART 1: PLACEMENT RATE BY DEPARTMENT (Horizontal Bar Chart)
    # -------------------------------------------------------------
    print("Generating Chart 1: Placement Rate by Department...")
    query_1 = """
        SELECT 
            s.department,
            ROUND(
                (COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN s.student_id END)::NUMERIC / COUNT(DISTINCT s.student_id) * 100), 
                2
            ) AS placement_rate
        FROM students s
        LEFT JOIN offers o ON s.student_id = o.student_id
        GROUP BY s.department
        ORDER BY placement_rate ASC; -- ASC so the highest is at the top of horizontal bar
    """
    df_1 = pd.read_sql_query(query_1, conn)
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Plot horizontal bars with a clean teal/blue gradient or color
    bars = ax.barh(df_1['department'], df_1['placement_rate'], color='#1f77b4', edgecolor='none', height=0.6)
    
    # Add titles and labels
    ax.set_title('Placement Success Rate by Department (Graduation Year 2026)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Placement Rate (%)', fontsize=11, labelpad=10)
    ax.set_xlim(0, 100)
    
    # Add values on top of the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 1.5,                 # Position text slightly to the right of the bar end
            bar.get_y() + bar.get_height()/2, # Centered vertically in the bar
            f'{width:.1f}%',            # Display formatted percentage
            va='center', ha='left', fontsize=10, fontweight='bold', color='#333333'
        )
        
    plt.tight_layout()
    plt.savefig('charts/placement_rate_by_dept.png')
    plt.close()
    
    # -------------------------------------------------------------
    # CHART 2: SALARY TRENDS (Average vs Max Package by Department)
    # -------------------------------------------------------------
    print("Generating Chart 2: Salary Packages by Department...")
    query_2 = """
        SELECT 
            s.department,
            ROUND(AVG(o.package_lpa), 2) AS avg_package,
            MAX(o.package_lpa) AS max_package
        FROM students s
        JOIN offers o ON s.student_id = o.student_id
        WHERE o.accepted = TRUE
        GROUP BY s.department
        ORDER BY avg_package DESC;
    """
    df_2 = pd.read_sql_query(query_2, conn)
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Position of bars on the x-axis
    import numpy as np
    x = np.arange(len(df_2['department']))
    width = 0.35  # width of each bar
    
    # Plot average and max bars side by side
    bars_avg = ax.bar(x - width/2, df_2['avg_package'], width, label='Average Package', color='#2ca02c')
    bars_max = ax.bar(x + width/2, df_2['max_package'], width, label='Highest Package', color='#ff7f0e')
    
    # Add labels, titles, and custom x-axis tick labels
    ax.set_ylabel('Package (LPA - Lakhs Per Annum)', fontsize=11, labelpad=10)
    ax.set_title('Salary Packages Offered (Avg vs Max) by Department', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(df_2['department'], rotation=15, ha='right', fontsize=9)
    ax.legend(frameon=True, facecolor='white', edgecolor='none')
    
    # Add value labels on top of the bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='semibold')
                        
    add_value_labels(bars_avg)
    add_value_labels(bars_max)
    
    # Expand vertical limit slightly to fit data labels
    ax.set_ylim(0, max(df_2['max_package']) * 1.15)
    
    plt.tight_layout()
    plt.savefig('charts/salary_trends_by_dept.png')
    plt.close()
    
    # -------------------------------------------------------------
    # CHART 3: RECRUITER MARKET SHARE (Donut Chart for Top Companies)
    # -------------------------------------------------------------
    print("Generating Chart 3: Recruiter Share of Placements...")
    query_3 = """
        SELECT 
            c.name AS company_name,
            COUNT(o.offer_id) AS placements
        FROM companies c
        JOIN offers o ON c.company_id = o.company_id
        WHERE o.accepted = TRUE
        GROUP BY c.name
        ORDER BY placements DESC;
    """
    df_3 = pd.read_sql_query(query_3, conn)
    
    # Take top 5 companies and group the rest into "Others"
    top_5 = df_3.head(5).copy()
    others_count = df_3.iloc[5:]['placements'].sum()
    
    # Create a new DataFrame row for Others
    others_row = pd.DataFrame([{'company_name': 'Others', 'placements': others_count}])
    df_pie = pd.concat([top_5, others_row], ignore_index=True)
    
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    
    # Define custom professional color palette
    colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#d62728']
    
    # Plot standard pie chart
    wedges, texts, autotexts = ax.pie(
        df_pie['placements'], 
        labels=df_pie['company_name'], 
        autopct='%1.1f%%',
        startangle=140, 
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor='w') # Width parameter makes it a Donut chart!
    )
    
    # Styling text on the donut chart
    for text in texts:
        text.set_color('#333333')
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')
        autotext.set_color('#333333')
        
    ax.set_title('Placements Distribution by Recruiter (Market Share)', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('charts/top_hiring_companies.png')
    plt.close()
    
    # -------------------------------------------------------------
    # CHART 4: PLACEMENT FUNNEL GAP (Grouped Bar Chart)
    # -------------------------------------------------------------
    print("Generating Chart 4: Placement Funnel and Gap Analysis...")
    query_4 = """
        SELECT 
            s.department,
            COUNT(DISTINCT s.student_id) AS total,
            COUNT(DISTINCT CASE WHEN o.accepted = TRUE THEN o.student_id END) AS placed
        FROM students s
        LEFT JOIN applications a ON s.student_id = a.student_id
        LEFT JOIN offers o ON s.student_id = o.student_id AND o.accepted = TRUE
        GROUP BY s.department
        ORDER BY total DESC;
    """
    df_4 = pd.read_sql_query(query_4, conn)
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    x = np.arange(len(df_4['department']))
    width = 0.35
    
    # Plot registered students vs placed students
    bars_total = ax.bar(x - width/2, df_4['total'], width, label='Total Registered Students', color='#7f7f7f')
    bars_placed = ax.bar(x + width/2, df_4['placed'], width, label='Placed Students', color='#17becf')
    
    ax.set_ylabel('Number of Students', fontsize=11, labelpad=10)
    ax.set_title('Placement Gap: Registered vs Placed Students by Department', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(df_4['department'], rotation=15, ha='right', fontsize=9)
    ax.legend(frameon=True, facecolor='white', edgecolor='none')
    
    add_value_labels(bars_total)
    add_value_labels(bars_placed)
    
    ax.set_ylim(0, max(df_4['total']) * 1.15)
    
    plt.tight_layout()
    plt.savefig('charts/placement_funnel_by_dept.png')
    plt.close()
    
    print("✅ All 4 matplotlib charts generated and saved inside 'charts/' successfully!")
    conn.close()

if __name__ == "__main__":
    print("Starting placement data visualization...")
    generate_charts()
