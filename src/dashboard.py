# Import the main Dash class to create our web application
from dash import Dash
# Import html components to create standard web elements like headings and divisions (divs)
from dash import html

# Initialize the Dash application
# __name__ tells Dash where to look for supporting files if we had any
app = Dash(__name__)

# Define the layout of our application (what the user will see on the screen)
# html.Div creates a container for our content (like a box on the screen)
app.layout = html.Div(
    # The 'children' property holds all the elements inside this container
    children=[
        # html.H1 creates a main heading (the largest text size on a webpage)
        # We are setting the text to our project title
        html.H1(children='Campus Placement Analytics Dashboard'),
        
        # Another div to act as an empty placeholder where our charts will go later
        html.Div(children='Charts will go here in the next steps!')
    ]
)

# This standard Python line checks if we are running this script directly
if __name__ == '__main__':
    # Start the local development web server
    # debug=True allows the dashboard to automatically update if we change the code later
    app.run(debug=True)
