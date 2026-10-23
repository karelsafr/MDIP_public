"""Dash10: kombinace dvou filtrů.

Cíl: filtrovat současně podle regionu i kategorie.
Novinka: dva vstupy jednoho callbacku a ošetření prázdného výběru.
Zkusit: vyber Plzeň a Elektronika. V těchto datech taková objednávka není.
Prázdný výběr: tržby 0 Kč, počet 0, průměr neexistuje (zobrazíme pomlčku).
Spuštění: Run, http://127.0.0.1:8050. Po úpravě kódu Stop a znovu Run.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])
regiony = ["Všechny"] + sorted(df["region"].unique())
kategorie = ["Všechny"] + sorted(df["kategorie"].unique())


def vyber_data(region, kategorie):
    # Každé volání začíná celým df. "Všechny" příslušnou podmínku přeskočí.
    vyber = df
    if region != "Všechny":
        vyber = vyber.loc[vyber["region"] == region]
    if kategorie != "Všechny":
        # Druhá podmínka zužuje první výběr: obě podmínky musí platit současně.
        vyber = vyber.loc[vyber["kategorie"] == kategorie]
    return vyber


def format_kc(hodnota):
    return f"{hodnota:,.0f}".replace(",", " ") + " Kč"


def prazdny_graf(nadpis):
    # Vrátíme novou figuru se zprávou, aby nezůstal graf předchozího výběru.
    fig = go.Figure()
    fig.add_annotation(text="Pro tento výběr nejsou žádné objednávky.",
                       x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(title=nadpis, template="plotly_white")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def vytvor_graf_casu(data):
    # empty znamená nula řádků; tento stav řešíme před tvorbou běžného grafu.
    if data.empty:
        return prazdny_graf("Denní tržby")
    souhrn = data.groupby("datum", as_index=False)["trzba"].sum()
    return px.line(souhrn, x="datum", y="trzba", title="Denní tržby",
                   labels={"datum": "Datum", "trzba": "Tržby (Kč)"})


def vytvor_graf_regionu(data):
    if data.empty:
        return prazdny_graf("Tržby podle regionu")
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    return px.bar(souhrn, x="region", y="trzba", title="Tržby podle regionu",
                  labels={"region": "Region", "trzba": "Tržby (Kč)"})


def vytvor_kartu(nazev, id_hodnoty):
    return html.Div([html.P(nazev), html.H2(id=id_hodnoty)],
                    style={"border": "1px solid #ccd5df", "padding": "20px",
                           "borderRadius": "10px", "flex": "1 1 200px"})


app = Dash(__name__)
app.title = "Dash10: dva filtry"
app.layout = html.Div([
    html.H1("Přehled objednávek"),
    html.Div([
        html.Div([
            html.Label("Region", htmlFor="region"),
            dcc.Dropdown(id="region", options=regiony,
                         value="Všechny", clearable=False),
        ], style={"flex": "1 1 240px"}),
        html.Div([
            html.Label("Kategorie", htmlFor="kategorie"),
            dcc.Dropdown(id="kategorie", options=kategorie,
                         value="Všechny", clearable=False),
        ], style={"flex": "1 1 240px"}),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "16px"}),
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
    html.P("Zdroj: syntetická data. Částky zobrazujeme zaokrouhlené na celé Kč."),
], style={"fontFamily": "Arial, sans-serif", "padding": "24px"})


# Pořadí Inputů odpovídá parametrům region, kategorie.
@app.callback(
    Output("graf-cas", "figure"),
    Output("graf-region", "figure"),
    Output("kpi-trzby", "children"),
    Output("kpi-pocet", "children"),
    Output("kpi-prumer", "children"),
    Output("popis-vyberu", "children"),
    Input("region", "value"),
    Input("kategorie", "value"),
)
def aktualizuj_dashboard(region, kategorie):
    vyber = vyber_data(region, kategorie)
    trzby = format_kc(vyber["trzba"].sum())
    pocet = str(len(vyber))
    # Součet a počet prázdného výběru jsou nula, průměr není definován.
    if vyber.empty:
        prumer = "—"
    else:
        prumer = format_kc(vyber["trzba"].mean())
    popis = (f"Region: {region}. Kategorie: {kategorie}. "
             f"Zobrazeno {len(vyber)} objednávek.")
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
