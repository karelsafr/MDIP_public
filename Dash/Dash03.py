"""Dash03: první graf na stránce.

Cíl: vložit známý graf Plotly do aplikace Dash.
Novinka: dcc.Graph a jeho vlastnost figure.
Zkusit: změň nadpis grafu a jeho barvu.
Spuštění: Run, http://127.0.0.1:8050. Před dalším příkladem Stop.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])


def vytvor_graf_regionu(data):
    # Funkce vrací Figure. V aplikaci ji zobrazí dcc.Graph, proto zde není show().
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    return px.bar(
        souhrn, x="region", y="trzba",
        title="Tržby podle regionu",
        labels={"region": "Region", "trzba": "Tržby (Kč)"},
    )


app = Dash(__name__)
app.title = "Dash03: první graf"
# app.layout je strom komponent Dash. fig.layout by nastavoval samotný graf.
app.layout = html.Div([
    html.H1("Přehled objednávek"),
    dcc.Graph(
        id="graf-region",
        figure=vytvor_graf_regionu(df),
    ),
    html.P("Zdroj: syntetická data pro workshop."),
])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
