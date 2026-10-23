"""Dash08: filtr mění graf.

Cíl: vybrat část dat a vytvořit z ní nový graf.
Novinka: callback vrací figure namísto textu v children.
Zkusit: změň graf z denních tržeb na denní počet objednávek.
Spuštění: Run, http://127.0.0.1:8050. Před dalším příkladem Stop.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])
regiony = ["Všechny"] + sorted(df["region"].unique())


def vytvor_graf_casu(data):
    souhrn = data.groupby("datum", as_index=False)["trzba"].sum()
    return px.line(souhrn, x="datum", y="trzba", title="Denní tržby",
                   labels={"datum": "Datum", "trzba": "Tržby (Kč)"})


app = Dash(__name__)
app.title = "Dash08: filtrovaný graf"
app.layout = html.Div([
    html.H1("Denní tržby vybraného regionu"),
    html.Label("Region", htmlFor="region"),
    dcc.Dropdown(id="region", options=regiony, value="Všechny", clearable=False),
    dcc.Graph(id="graf-cas"),
    html.P("Zdroj: syntetická data pro workshop."),
], style={"maxWidth": "1100px", "margin": "24px auto",
          "fontFamily": "Arial, sans-serif"})


# Novinkou je Output do vlastnosti figure: callback vrací celý graf Plotly.
@app.callback(
    Output("graf-cas", "figure"),
    Input("region", "value"),
)
def aktualizuj_graf(region):
    if region == "Všechny":
        vyber = df
    else:
        # Porovnání dá pro každý řádek True/False. loc ponechá řádky s True.
        maska = df["region"] == region
        vyber = df.loc[maska]
    # Původní df nepřepisujeme: po návratu na Všechny máme stále celý soubor.
    return vytvor_graf_casu(vyber)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
