"""Dash11: vzhled dashboardu.

Cíl: sjednotit vzhled již fungující aplikace.
Novinka: připravené slovníky stylů a společná úprava vzhledu grafů.
Zkusit: změň AKCENT a pozoruj, které části se změní.
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

AKCENT = "#087f8c"
# Styl je Python slovník. Víceslovné CSS vlastnosti mají podobu backgroundColor.
# gap je mezera mezi dětmi; padding je vnitřní odsazení jedné komponenty.
STYL_RADKU = {"display": "flex", "flexWrap": "wrap", "gap": "18px"}
STYL_KARTY = {
    "backgroundColor": "white",
    "padding": "22px",
    "borderRadius": "12px",
    "borderTop": f"4px solid {AKCENT}",
    "boxShadow": "0 2px 8px #10243b12",
    "flex": "1 1 200px",
}


def vyber_data(region, kategorie):
    # Druhý filtr zužuje výsledek prvního, původní df zůstává celý.
    vyber = df
    if region != "Všechny":
        vyber = vyber.loc[vyber["region"] == region]
    if kategorie != "Všechny":
        vyber = vyber.loc[vyber["kategorie"] == kategorie]
    return vyber


def format_kc(hodnota):
    return f"{hodnota:,.0f}".replace(",", " ") + " Kč"


def prazdny_graf(nadpis):
    fig = go.Figure()
    fig.add_annotation(text="Pro tento výběr nejsou žádné objednávky.",
                       x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(title=nadpis, template="plotly_white")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return uprav_graf(fig)


def uprav_graf(fig):
    # Vzhled figury nastavuje Plotly. Style u html.Div upravuje webovou stránku.
    fig.update_layout(template="plotly_white", font_family="Arial",
                      font_color="#19324d", paper_bgcolor="white",
                      margin=dict(l=60, r=20, t=65, b=55), height=360,
                      separators=", ", title_font_size=20)
    fig.update_yaxes(gridcolor="#e8edf2", rangemode="tozero")
    return fig


def vytvor_graf_casu(data):
    if data.empty:
        return prazdny_graf("Denní tržby")
    souhrn = data.groupby("datum", as_index=False)["trzba"].sum()
    fig = px.line(souhrn, x="datum", y="trzba", title="Denní tržby",
                  labels={"datum": "Datum", "trzba": "Tržby (Kč)"})
    fig.update_traces(line_color=AKCENT)
    return uprav_graf(fig)


def vytvor_graf_regionu(data):
    if data.empty:
        return prazdny_graf("Tržby podle regionu")
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    fig = px.bar(souhrn, x="region", y="trzba", title="Tržby podle regionu",
                 labels={"region": "Region", "trzba": "Tržby (Kč)"})
    fig.update_traces(marker_color=AKCENT)
    return uprav_graf(fig)


def vytvor_kartu(nazev, id_hodnoty):
    return html.Div([html.P(nazev), html.H2(id=id_hodnoty)],
                    style=STYL_KARTY)


app = Dash(__name__)
app.title = "Dash11: vzhled dashboardu"
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
    ], style=STYL_RADKU),
    html.P(id="popis-vyberu"),
    html.Div([
        vytvor_kartu("Tržby", "kpi-trzby"),
        vytvor_kartu("Počet objednávek", "kpi-pocet"),
        vytvor_kartu("Průměrná objednávka", "kpi-prumer"),
    ], style=STYL_RADKU),
    html.Div([
        dcc.Graph(id="graf-cas", style={"flex": "1 1 420px", "minWidth": 0, "borderRadius": "12px",
                         "overflow": "hidden", "marginTop": "20px"}),
        dcc.Graph(id="graf-region", style={"flex": "1 1 420px", "minWidth": 0, "borderRadius": "12px",
                         "overflow": "hidden", "marginTop": "20px"}),
    ], style=STYL_RADKU),
    html.P("Zdroj: syntetická data. Částky zobrazujeme zaokrouhlené na celé Kč."),
], style={"fontFamily": "Arial, sans-serif", "padding": "28px",
          "color": "#19324d", "backgroundColor": "#f2f5f9",
          "maxWidth": "1280px", "margin": "0 auto"})


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
