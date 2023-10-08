# All my tutorials on https://www.youtube.com/channel/UCqBFsuAz41sqWcFjZkqmJqQ/featured
import dash
from dash import Dash, html, dcc, dash_table, Input, Output,State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from flask import Flask
from flask_sqlalchemy import SQLAlchemy




# app requires "pip install psycopg2" as well

server = Flask(__name__)
app = Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# for your home PostgreSQL test table
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:PGPassword001@localhost/crud_dash"

# for your live Heroku PostgreSQL database
# app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgres://kcfwfqwznavpjq:9473936daf43bff3d17c1dd8ab2c28144dfbf677\
# 14cb30622e3017bbe55cdeac@ec2-34-197-188-147.compute-1.amazonaws.com:5432/d9eat64jon4dti"

db = SQLAlchemy(app.server)


class Product(db.Model):
    __tablename__ = 'ziltektable'

    MK_Type = db.Column(db.String(40), nullable=False, primary_key=True)
    Sheet = db.Column(db.String(40), nullable=False)
    Client = db.Column(db.String(40), nullable=False)
    Country = db.Column(db.String(40), nullable=False)
    Service_date = db.Column(db.Date, nullable=False)
    Reason_for_Service = db.Column(db.String(40), nullable=False)
    RemScan_Serial = db.Column(db.String(40), nullable=False)
    User_ID = db.Column(db.String(40), nullable=False)
    User_Password = db.Column(db.String(40), nullable=False)
    Background_Cap = db.Column(db.Float, nullable=False)
    Polystyrene_PS_Cap = db.Column(db.Float, nullable=False)
    SNR_1142_1042_cm1 = db.Column(db.Float, nullable=False)
    SNR_2600_2500_cm1 = db.Column(db.Float, nullable=False)
    Centre_burst_intensity = db.Column(db.Float, nullable=False)
    Single_beam_spectrum_4200_4500 = db.Column(db.Float, nullable=False)
    Single_beam_spectrum_2600_3000 = db.Column(db.Float, nullable=False)

    def __init__(self, mk_type,
        sheet,
        client,
        country,
        service_date,
        reason_for_service,
        remscan_serial,
        user_id,
        user_password,
        background_cap,
        polystyrene_ps_cap,
        snr_1142,
        snr_2600,
        centre_burst,
        single_beam_4200,
        single_beam_2600):
            self.MK_Type = mk_type
            self.Sheet = sheet
            self.Client = client
            self.Country = country
            self.Service_date = service_date
            self.Reason_for_Service = reason_for_service
            self.RemScan_Serial = remscan_serial
            self.User_ID = user_id
            self.User_Password = user_password
            self.Background_Cap = background_cap
            self.Polystyrene_PS_Cap = polystyrene_ps_cap
            self.SNR_1142_1042_cm1 = snr_1142
            self.SNR_2600_2500_cm1 = snr_2600
            self.Centre_burst_intensity = centre_burst
            self.Single_beam_spectrum_4200_4500 = single_beam_4200
            self.Single_beam_spectrum_2600_3000 = single_beam_2600
        # self.Phone = phone
        # self.Version = version
        # self.Price = price
        # self.Sales = sales


# ------------------------------------------------------------------------------------------------

app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='adding-rows-name',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10}
        ),
        html.Button('Add Column', id='adding-columns-button', n_clicks=0)
    ], style={'height': 50}),

    dcc.Interval(id='interval_pg', interval=86400000*7, n_intervals=0),  # activated once/week or when page refreshed
    html.Div(id='postgres_datatable'),

    html.Button('Add Row', id='editing-rows-button', n_clicks=0),
    html.Button('Save to PostgreSQL', id='save_to_postgres', n_clicks=0),

    # Create notification when saving to excel
    html.Div(id='placeholder', children=[]),
    dcc.Store(id="store", data=0),
    dcc.Interval(id='interval', interval=1000),

    dcc.Graph(id='my_graph')

])


# ------------------------------------------------------------------------------------------------


@app.callback(Output('postgres_datatable', 'children'),
              [Input('interval_pg', 'n_intervals')])
def populate_datatable(n_intervals):
    df = pd.read_sql_table('ziltektable', con=db.engine)
    return [
        dash_table.DataTable(
            id='our-table',
            columns=[{
                         'name': str(x),
                         'id': str(x),
                         'deletable': False,
                     } if x == 'MK_Type' or x == 'Sheet'
                     else {
                'name': str(x),
                'id': str(x),
                'deletable': True,
            }
                     for x in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            filter_action="native",
            sort_action="native",  # give user capability to sort columns
            sort_mode="single",  # sort across 'multi' or 'single' columns
            page_action='none',  # render all of the data at once. No paging.
            style_table={'height': '300px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'right'
                } for c in ['Price', 'Sales']
            ]

        ),
    ]


@app.callback(
    Output('our-table', 'columns'),
    [Input('adding-columns-button', 'n_clicks')],
    [State('adding-rows-name', 'value'),
     State('our-table', 'columns')],
    prevent_initial_call=True)
def add_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'name': value, 'id': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns


@app.callback(
    Output('our-table', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('our-table', 'data'),
     State('our-table', 'columns')],
    prevent_initial_call=True)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

# Add a callback to update 'my_graph' data when 'our-table' data changes
@app.callback(
    Output('my_graph', 'figure'),
    [Input('our-table', 'data')],
    prevent_initial_call=True)

def display_graph(data):
    df_fig = pd.DataFrame(data)
    fig = px.bar(df_fig, x='MK_Type', y='Background_Cap')
    return fig


@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_postgres', 'n_clicks'),
     Input("interval", "n_intervals")],
    [State('our-table', 'data'),
     State('store', 'data')],
    prevent_initial_call=True)
def df_to_csv(n_clicks, n_intervals, dataset, s):
    output = html.Plaintext("The data has been saved to your PostgreSQL database.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_triggered == "save_to_postgres":
        s = 6
        pg = pd.DataFrame(dataset)
        pg.to_sql("ziltektable", con=db.engine, if_exists='replace', index=False)
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s - 1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s


if __name__ == '__main__':
    app.run_server(debug=True)