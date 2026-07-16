# 🎓 Campus Placement Analyzer

A full-stack, data-driven web application designed to analyze and visualize campus placement data. Built with PostgreSQL (ShaktiDB), Python, and Plotly Dash.

## Features

- **End-to-End Data Pipeline**: Generates massive realistic datasets and safely stores them in a local PostgreSQL database.
- **Advanced SQL Analytics**: Uses optimized SQL queries to generate insights like placement rates, average salary packages, and company hiring trends.
- **Interactive Dashboard**: A clean, professionally styled web dashboard built with Plotly Dash that allows users to dynamically filter data by Graduation Year and Department.

## Dashboard Charts

1. **Placement Rate by Department** (Bar Chart)
2. **Average Package Trend Over Time** (Line Chart)
3. **Top 5 Hiring Companies** (Horizontal Bar Chart)
4. **Applied vs Placed Gap** (Grouped Bar Chart)

## Setup Instructions

### 1. Requirements
Ensure you have Python 3 installed. You will also need PostgreSQL running locally (this project specifically uses ShaktiDB).

### 2. Installation
Clone the repository, create a virtual environment, and install the required dependencies:

```bash
git clone https://github.com/eileen-7/campus_placement_analytics.git
cd campus_placement_analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Database Setup
Create the PostgreSQL tables and generate the synthetic data:

```bash
python3 src/schema.py
python3 src/generate_data.py
```

### 4. Run the Dashboard
Start the local server to view the interactive dashboard:

```bash
python3 src/dashboard.py
```

Once running, open your browser and navigate to `http://localhost:8050/`.
