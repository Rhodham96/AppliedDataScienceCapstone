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
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 
                                                'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',  
                                                options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                                ],
                                                value='ALL',
                                                placeholder='Select a Launch Site here',
                                                searchable=True            
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                                id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={i: f'{i} kg' for i in range(0, 11000, 1000)},  # Adding marks every 1000 kg
                                                value=[min_payload, max_payload]  # Set the initial range to the min and max payload
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                

                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
# Callback function for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    print(f"Dropdown selection: {selected_site}")
    if selected_site == 'ALL':
        # Pie chart for all sites showing total success launches
        fig = px.pie(
            spacex_df,
            names='Launch Site',  # Categories for the pie chart
            values='class',  # Success launches are represented by the 'class' column
            title='Total Successful Launches by Site'
        )
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

        # Count successes and failures
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]

        # Create a dataframe for the pie chart
        pie_data = pd.DataFrame({
            'Outcome': ['Success', 'Failure'],
            'Count': [success_count, failure_count]
        })

        # Create the pie chart
        fig = px.pie(
            pie_data,
            names='Outcome',
            values='Count',
            title=f'Total Success vs Failure Launches for Site {selected_site}'
        )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter the dataframe based on the payload range
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',  # Color by Booster Version
            title='Payload vs. Outcome for All Sites',
            labels={'class': 'Mission Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        )
    else:
        # Filter dataframe for the selected site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        # Scatter plot for the selected site
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',  # Color by Booster Version
            title=f'Payload vs. Outcome for Site {selected_site}',
            labels={'class': 'Mission Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        )
    return fig

# Run the app
print(spacex_df.head())
print(spacex_df['Launch Site'].unique())
if __name__ == '__main__':
    app.run_server()

