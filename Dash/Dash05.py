"""Dash05: kartičky s ukazateli.

Cíl: doplnit souhrnné hodnoty vypočtené z dat.
Novinka: tři karty a opakovaně použitelná funkce vytvor_kartu().
Zkusit: přidej kartu s mediánem hodnoty objednávky.
Spuštění: Run, http://127.0.0.1:8050. Před dalším příkladem Stop.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])


def format_kc(hodnota):
    # Až hotové číslo převádíme na text pro zobrazení; výpočty používají čísla.
    return f"{hodnota:,.0f}".replace(",", " ") + " Kč"


def vytvor_kartu(nazev, hodnota, id_hodnoty):
    return html.Div(
        [
            html.P(nazev),
            html.H2(hodnota, id=id_hodnoty),
        ],
        style={"border": "1px solid #ccd5df", "padding": "20px",
               "borderRadius": "10px", "flex": "1 1 200px"},
    )


def vytvor_graf_casu(data):
    souhrn = data.groupby("datum", as_index=False)["trzba"].sum()
    return px.line(souhrn, x="datum", y="trzba", title="Denní tržby",
                   labels={"datum": "Datum", "trzba": "Tržby (Kč)"})


def vytvor_graf_regionu(data):
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    return px.bar(souhrn, x="region", y="trzba", title="Tržby podle regionu",
                  labels={"region": "Region", "trzba": "Tržby (Kč)"})


# Jeden řádek CSV je jedna objednávka. Nejprve spočítáme tři číselné hodnoty.
trzby = df["trzba"].sum()
pocet = len(df)
prumer = df["trzba"].mean()

app = Dash(__name__)
app.title = "Dash05: souhrnné karty"
app.layout = html.Div([
    html.H1("Přehled objednávek"),
    html.Div([
        vytvor_kartu("Tržby", format_kc(trzby), "kpi-trzby"),
        vytvor_kartu("Počet objednávek", str(pocet), "kpi-pocet"),
        vytvor_kartu("Průměrná objednávka", format_kc(prumer),
                     "kpi-prumer"),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "16px"}),
    html.Div([
        dcc.Graph(id="graf-cas", figure=vytvor_graf_casu(df),
                  style={"flex": "1 1 420px", "minWidth": 0}),
        dcc.Graph(id="graf-region", figure=vytvor_graf_regionu(df),
                  style={"flex": "1 1 420px", "minWidth": 0}),
    ], style={"display": "flex", "flexWrap": "wrap"}),
    html.P("Jedna objednávka odpovídá jednomu řádku. Zdroj: syntetická data."),
], style={"fontFamily": "Arial, sans-serif", "padding": "24px"})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
