# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# App Layout
# ─────────────────────────────────────────────────────────────────────────────
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # ── TASK 1: Dropdown to select launch site ────────────────────────────────
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
        ] + [
            {'label': site, 'value': site}
            for site in sorted(spacex_df['Launch Site'].unique())
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # ── TASK 3: Range Slider to select payload ────────────────────────────────
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 11000, 1000)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# ─────────────────────────────────────────────────────────────────────────────
# TASK 2: Callback – Pie Chart (success rate by site)
# ─────────────────────────────────────────────────────────────────────────────
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Total successful launches across all sites
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Filter for the selected site and show success vs failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['Outcome'] = outcome_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            outcome_counts,
            values='count',
            names='Outcome',
            title=f'Total Launch Outcomes for {entered_site}',
            color='Outcome',
            color_discrete_map={'Success': 'green', 'Failure': 'red'}
        )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# TASK 4: Callback – Scatter Chart (payload vs. class, colored by booster)
# ─────────────────────────────────────────────────────────────────────────────
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    mask = (
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    )
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation Between Payload and Success for All Sites',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation Between Payload and Success for {entered_site}',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
        )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Run the app
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=8050)
