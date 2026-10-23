"""Dash09: jeden filtr aktualizuje celý dashboard.

Cíl: odvodit karty i grafy ze stejného výběru dat.
Novinka: jeden callback má několik výstupů. Pořadí return odpovídá Output.
Zkusit: ověř tržby pro Prahu součtem stejného výběru v Pythonu.
Spuštění: Run, http://127.0.0.1:8050. Po úpravě kódu Stop a znovu Run.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])
regiony = ["Všechny"] + sorted(df["region"].unique())


def vyber_data(region):
    # Vracíme výběr pro aktuální požadavek; globální df se nemění.
    if region == "Všechny":
        return df
    return df.loc[df["region"] == region]


def format_kc(hodnota):
    return f"{hodnota:,.0f}".replace(",", " ") + " Kč"


def vytvor_kartu(nazev, id_hodnoty):
    return html.Div([
        html.P(nazev), html.H2(id=id_hodnoty),
    ], style={"border": "1px solid #ccd5df", "padding": "20px",
              "borderRadius": "10px", "flex": "1 1 200px"})


def vytvor_graf_casu(data):
    souhrn = data.groupby("datum", as_index=False)["trzba"].sum()
    return px.line(souhrn, x="datum", y="trzba", title="Denní tržby",
                   labels={"datum": "Datum", "trzba": "Tržby (Kč)"})


def vytvor_graf_regionu(data):
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    return px.bar(souhrn, x="region", y="trzba", title="Tržby podle regionu",
                  labels={"region": "Region", "trzba": "Tržby (Kč)"})


app = Dash(__name__)
app.title = "Dash09: propojený dashboard"
app.layout = html.Div([
    html.H1("Přehled objednávek"),
    html.Label("Region", htmlFor="region"),
    dcc.Dropdown(id="region", options=regiony, value="Všechny", clearable=False),
    html.P(id="popis-vyberu"),
    html.Div([
        vytvor_kartu("Tržby", "kpi-trzby"),
        vytvor_kartu("Počet objednávek", "kpi-pocet"),
        vytvor_kartu("Průměrná objednávka", "kpi-prumer"),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "16px"}),
    html.Div([
        dcc.Graph(id="graf-cas", style={"flex": "1 1 420px", "minWidth": 0}),
        dcc.Graph(id="graf-region", style={"flex": "1 1 420px", "minWidth": 0}),
    ], style={"display": "flex", "flexWrap": "wrap"}),
    html.P("Zdroj: syntetická data. Peněžní ukazatele zaokrouhlujeme na celé Kč."),
], style={"fontFamily": "Arial, sans-serif", "padding": "24px"})


# Šest Outputů má stejné pořadí jako šest hodnot v return na konci funkce.
@app.callback(
    Output("graf-cas", "figure"),
    Output("graf-region", "figure"),
    Output("kpi-trzby", "children"),
    Output("kpi-pocet", "children"),
    Output("kpi-prumer", "children"),
    Output("popis-vyberu", "children"),
    Input("region", "value"),
)
def aktualizuj_dashboard(region):
    vyber = vyber_data(region)
    trzby = format_kc(vyber["trzba"].sum())
    pocet = str(len(vyber))
    if vyber.empty:
        prumer = "—"
    else:
        prumer = format_kc(vyber["trzba"].mean())
    popis = f"Region: {region}. Zobrazeno {len(vyber)} objednávek."
    return (
        vytvor_graf_casu(vyber),     # 1: graf-cas.figure
        vytvor_graf_regionu(vyber),  # 2: graf-region.figure
        trzby,                     # 3: kpi-trzby.children
        pocet,                     # 4: kpi-pocet.children
        prumer,                    # 5: kpi-prumer.children
        popis,                     # 6: popis-vyberu.children
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
