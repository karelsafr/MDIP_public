"""Dash04: dva grafy na stránce.

Cíl: uspořádat několik komponent do společného rozvržení.
Novinka: obal html.Div a jednoduché styly flex / flexWrap.
Zkusit: změň mezeru mezi grafy nebo jejich minimální šířku.
Spuštění: Run, http://127.0.0.1:8050. Před dalším příkladem Stop.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])


def vytvor_graf_casu(data):
    souhrn = data.groupby("datum", as_index=False)["trzba"].sum()
    return px.line(
        souhrn, x="datum", y="trzba", title="Denní tržby",
        labels={"datum": "Datum", "trzba": "Tržby (Kč)"},
    )


def vytvor_graf_regionu(data):
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    return px.bar(
        souhrn, x="region", y="trzba", title="Tržby podle regionu",
        labels={"region": "Region", "trzba": "Tržby (Kč)"},
    )


app = Dash(__name__)
app.title = "Dash04: rozvržení stránky"
# Dvě komponenty Graph mají každá vlastní figuru; nejde o Plotly subploty.
# Obalový Div s display="flex" řadí své děti vedle sebe.
# flexWrap="wrap" dovolí přesun pod sebe a gap určuje mezeru mezi grafy.
# flex="1 1 420px" jim dává výchozí šířku 420 px a dovoluje změnu velikosti.
app.layout = html.Div([
    html.H1("Přehled objednávek"),
    html.Div([
        dcc.Graph(id="graf-cas", figure=vytvor_graf_casu(df),
                  style={"flex": "1 1 420px", "minWidth": 0}),
        dcc.Graph(id="graf-region", figure=vytvor_graf_regionu(df),
                  style={"flex": "1 1 420px", "minWidth": 0}),
    ], style={
        "display": "flex",
        "flexWrap": "wrap",
        "gap": "20px",
    }),
    html.P("Zdroj: syntetická data pro workshop."),
])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
