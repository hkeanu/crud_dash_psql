import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable
import plotly.graph_objects as go

df = pd.DataFrame(
    {"values": [1, 2, 3, 4], "labels": ["value 1", "value 2", "value 3", "value 4"]}
)

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="graph"),
        DataTable(
            id="table",
            columns=[{"name": "values", "id": "values"}],
            data=df.to_dict("records"),
        ),
    ]
)


@app.callback(
    Output("graph", "figure"), Input("table", "active_cell"), prevent_initial_call=True
)
def update_output_div(active_cell):
    selected_value = df.iloc[active_cell["row"], active_cell["column"]]
    num_values = len(df["values"])

    fig = go.Figure(go.Bar(x=[selected_value], y=[selected_value]))
    fig.update_layout(yaxis_range=[0, num_values])

    fig.update_layout(
        yaxis=dict(
            tickmode="array",
            tickvals=df["values"],
            ticktext=df["labels"],
        ),
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[selected_value],
            ticktext=[selected_value],
        )
    )

    return fig


if __name__ == "__main__":
    app.run_server()