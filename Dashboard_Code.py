import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px


data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')


app = dash.Dash(__name__)

dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]

year_list = [i for i in range(1980, 2024, 1)]


app.layout = html.Div([
    html.H1('Automobile Sales Statistics Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            value='Select Statistics',
            placeholder='Select a report type'
        )
    ]),
    html.Div(dcc.Dropdown(
        id='select-year',
        options=[{'label': i, 'value': i} for i in year_list],
        value='Select Statistics'
    )),
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'grid'}),])
])

@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics',component_property='value'))

def update_input_container(selected_statistics):
    if selected_statistics =='Yearly Statistics': 
        return False
    else: 
        return True

# Callback for plotting
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='select-year', component_property='value'), Input(component_id='dropdown-statistics', component_property='value')])

def update_output_container(input_year, selected_statistics):
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        # Plot 1 Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec=recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                x='Year',
                y='Automobile_Sales',
                title="Average Automobile Sales fluctuation over Recession Period"))

        # Plot 2 Calculate the average number of vehicles sold by vehicle type       
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()                           
        R_chart2  = dcc.Graph(
            figure=px.bar(average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title='Average Automobile Sales per Vehicle Type over Recession Period'))

        # Plot 3 Pie chart for total expenditure share by vehicle type during recessions
        exp_rec=recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, 
                values='Advertising_Expenditure', 
                names='Vehicle_Type', 
                title='Total Expenditure Share by Vehicle Type during Recessions'))

        # Plot 4 bar chart for the effect of unemployment rate on vehicle type and sales
        urate_rec=recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])['Automobile_Sales'].count().reset_index()
        R_chart4 = dcc.Graph(
            figure = px.bar(urate_rec,
                x='unemployment_rate',
                y='Automobile_Sales',
                labels={'Automobile_Sales': 'Count of Automobile Sales'},
                color='Vehicle_Type',
                barmode='group',
                title='Effect of Unemployment Rate on Vehicle Type and Sales during the Recession Period'
            )
        )

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1),html.Div(children=R_chart2)],style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3),html.Div(children=R_chart4)],style={'display': 'flex'})
            ]

    # Yearly Statistic Report Plots                             
    elif (input_year and selected_statistics=='Yearly Statistics') :
        yearly_data = data[data['Year'] == input_year]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                     
        # plot 1 Yearly Automobile sales using line chart for the whole period.
        yas= data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas,
                x='Year',
                y='Automobile_Sales',
                title="Average Automobile Sales from 1980 to 2023"))
            
        # Plot 2 Total Monthly Automobile sales using line chart.
        monthly_data = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        monthly_data['Month'] = pd.Categorical(monthly_data['Month'], categories=months, ordered=True)
        monthly_data.sort_values(by='Month', inplace=True)
        Y_chart2 = dcc.Graph(
            figure=px.line(monthly_data,
                x='Month',
                y='Automobile_Sales',
                title="Total Monthly Automobile Sales for {}".format(input_year)))

        # Plot 3 bar chart for average number of vehicles sold during the given year
        avr_vdata=yearly_data.groupby(['Month', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata,
                x='Month',
                y='Automobile_Sales',
                labels={'Automobile_Sales': 'Average Automobile Sales'},
                color='Vehicle_Type',
                category_orders={'Month': months},
                title='Average Vehicles Sold by Vehicle Type in the year {}'.format(input_year)))

        # Plot 4 Total Advertisement Expenditure for each vehicle using pie chart
        exp_data=yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                values='Advertising_Expenditure', 
                names='Vehicle_Type', 
                title='Total Expenditure Share by Vehicle Type in {}'.format(input_year)))

        return [
            html.Div(className='chart-item', children=[html.Div(children=Y_chart1),html.Div(children=Y_chart2)],style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=Y_chart3),html.Div(children=Y_chart4)],style={'display': 'flex'})
        ]
        
    else:
        return None


if __name__ == '__main__':
    app.run_server(debug=True)
