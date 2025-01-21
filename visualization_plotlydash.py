# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': launch_site, 'value': launch_site} for launch_site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
    id='payload-slider',
    min=0, 
    max=10000, 
    step=1000,
    marks={i: f'{i} Kg' for i in range(0, 10001, 1000)},  # Create marks from 0 to 10000 Kg with step 1000
    value=[0, 10000]  # Set the initial selected range from 0 to 10000 Kg
),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # If no site is selected, use the entire dataframe
    filtered_df = spacex_df

    # If 'ALL' sites are selected, use the entire dataframe to show total successful launches
    if entered_site == 'ALL':
        # Count the success and failure in the 'class' column, where class=1 is success and class=0 is failure
        fig = px.pie(
            filtered_df, 
            names='class', 
            title='Total Launch Success vs. Failure (All Sites)', 
            labels={'class': 'Launch Outcome'}, 
            color='class', 
            color_discrete_map={0: 'red', 1: 'green'},
            hole=0.3  # Makes it a donut chart
        )
        return fig
    else:
        # Filter the dataframe based on the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Count the success and failure for the selected site
        fig = px.pie(
            filtered_df, 
            names='class', 
            title=f'Launch Success vs. Failure for {entered_site}', 
            labels={'class': 'Launch Outcome'}, 
            color='class', 
            color_discrete_map={0: 'red', 1: 'green'},
            hole=0.3  # Makes it a donut chart
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(entered_site, payload_range):
    # Filter the data based on the selected payload range
    min_payload, max_payload = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                            (spacex_df['Payload Mass (kg)'] <= max_payload)]

    # Check if 'ALL' sites are selected
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload Mass and Launch Outcome (All Sites)',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (Kg)'},
            color_discrete_map={'v1.0': 'blue', 'v1.1': 'green', 'FT': 'red', 'Block 5': 'purple'}
        )
        return fig
    else:
        # Filter data based on the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Scatter plot for the selected launch site
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload Mass and Launch Outcome for {entered_site}',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (Kg)'},
            color_discrete_map={'v1.0': 'blue', 'v1.1': 'green', 'FT': 'red', 'Block 5': 'purple'}
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
