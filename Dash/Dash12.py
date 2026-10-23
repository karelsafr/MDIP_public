"""Dash12: hotový dashboard nad objednávkami.

Cíl: spojit známé kroky do přehledné samostatné aplikace.
Novinka: ucelená aplikace a doplnění dnů bez objednávek do časového grafu.
Zkusit: přidej čtvrtou kartu s mediánem a zapoj ji do callbacku.
Ověření: Plzeň + Elektronika vrací prázdný výběr, všechny filtry obnoví data.
Spuštění: Run, http://127.0.0.1:8050. Po úpravě kódu Stop a znovu Run.
Data jsou syntetická. Jedna objednávka patří právě jednomu regionu a kategorii.

Mapa souboru: 1. data, 2. grafy, 3. komponenty a layout, 4. callback, 5. server.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

# 1. Data a společný vzhled
SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])
regiony = ["Všechny"] + sorted(df["region"].unique())
kategorie = ["Všechny"] + sorted(df["kategorie"].unique())
obdobi = f"{df['datum'].min():%d. %m. %Y} až {df['datum'].max():%d. %m. %Y}"
AKCENT = "#087f8c"
TMAVA = "#19324d"
STYL_RADKU = {"display": "flex", "flexWrap": "wrap", "gap": "18px"}
STYL_KARTY = {"backgroundColor": "white", "borderRadius": "12px",
              "padding": "22px", "flex": "1 1 210px", "minWidth": 0,
              "borderTop": f"4px solid {AKCENT}",
              "boxShadow": "0 2px 8px #10243b10"}


def vyber_data(region, kategorie):
    """Obě podmínky platí současně. Původní df neměníme."""
    vyber = df
    if region != "Všechny":
        vyber = vyber.loc[vyber["region"] == region]
    if kategorie != "Všechny":
        # Kategorie dále zužuje vybraný region: jde o průnik obou podmínek.
        vyber = vyber.loc[vyber["kategorie"] == kategorie]
    return vyber


def format_kc(hodnota):
    return f"{hodnota:,.0f}".replace(",", " ") + " Kč"


# 2. Grafy. Každá funkce dostane již vyfiltrovaná data.
def uprav_graf(fig):
    fig.update_layout(
        template="plotly_white", font=dict(family="Arial", color=TMAVA, size=13),
        paper_bgcolor="white", plot_bgcolor="white", height=360,
        margin=dict(l=65, r=25, t=65, b=60), separators=", ",
        title_font_size=20, showlegend=False,
    )
    fig.update_yaxes(gridcolor="#e8edf2", rangemode="tozero")
    return fig


def prazdny_graf(nadpis):
    fig = go.Figure()
    fig.add_annotation(text="Pro tento výběr nejsou objednávky.<br>Změňte filtry.",
                       x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(size=16, color="#61738a"))
    fig.update_layout(title=nadpis)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return uprav_graf(fig)


def vytvor_graf_casu(data):
    if data.empty:
        return prazdny_graf("Denní tržby")
    # Nový datový krok oproti Dash11: zachováme všechny dny celého období.
    # Náš soubor obsahuje všechny výukové objednávky. Chybějící den po filtraci
    # tedy znamená žádnou objednávku pro tento výběr, a proto nulovou tržbu.
    # U neúplných měření by takové automatické doplnění nul nebylo oprávněné.
    vsechny_dny = pd.date_range(df["datum"].min(), df["datum"].max(), name="datum")
    souhrn = data.groupby("datum")["trzba"].sum()
    souhrn = souhrn.reindex(vsechny_dny, fill_value=0)
    # Datum bylo indexem souhrnu; reset_index ho vrátí do běžného sloupce.
    souhrn = souhrn.rename("trzba").reset_index()
    fig = px.line(souhrn, x="datum", y="trzba", title="Denní tržby",
                  labels={"datum": "Datum", "trzba": "Tržby (Kč)"})
    fig.update_traces(line=dict(color=AKCENT, width=2),
                      hovertemplate="%{x|%d. %m. %Y}<br>%{y:,.0f} Kč<extra></extra>")
    fig.update_xaxes(tickformat="%d. %m.")
    return uprav_graf(fig)


def vytvor_graf_regionu(data):
    if data.empty:
        return prazdny_graf("Tržby podle regionu")
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    fig = px.bar(souhrn, x="region", y="trzba", title="Tržby podle regionu",
                 labels={"region": "Region", "trzba": "Tržby (Kč)"},
                 category_orders={"region": regiony[1:]})
    fig.update_traces(marker_color=AKCENT,
                      hovertemplate="%{x}<br>%{y:,.0f} Kč<extra></extra>")
    return uprav_graf(fig)


# 3. Komponenty a rozvržení stránky
# app.layout skládá webové komponenty; vzhled os a sérií patří figurám Plotly.
def vytvor_kartu(nazev, id_hodnoty, vysvetleni):
    return html.Div([
        html.P(nazev, style={"margin": "0 0 12px", "color": "#61738a"}),
        html.Div(id=id_hodnoty,
                 style={"fontSize": "32px", "fontWeight": "700", "color": TMAVA}),
        html.P(vysvetleni, style={"fontSize": "13px", "color": "#61738a",
                                 "margin": "10px 0 0"}),
    ], style=STYL_KARTY)


def vytvor_filtr(nazev, id_prvku, moznosti):
    return html.Div([
        html.Label(nazev, htmlFor=id_prvku,
                   style={"display": "block", "fontWeight": "700", "marginBottom": "8px"}),
        dcc.Dropdown(id=id_prvku, options=moznosti,
                     value="Všechny", clearable=False),
    ], style={"flex": "1 1 230px", "minWidth": 0})


app = Dash(__name__)
app.title = "Objednávky v přehledu"
app.layout = html.Div([
    html.Header([
        html.P("PYTHON / PLOTLY / DASH", style={"color": "#85d4d3", "fontSize": "13px",
                                              "fontWeight": "700", "letterSpacing": "2px"}),
        html.H1("Objednávky v přehledu", style={"fontSize": "36px", "margin": "10px 0"}),
        html.P(f"{obdobi}. Syntetická data pro workshop.",
               style={"color": "#cad7e5", "margin": 0}),
    ], style={"backgroundColor": TMAVA, "color": "white", "padding": "30px",
              "borderRadius": "14px", "marginBottom": "22px"}),
    html.Div([
        html.Div([
            vytvor_filtr("Region", "region", regiony),
            vytvor_filtr("Kategorie", "kategorie", kategorie),
        ], style=STYL_RADKU),
        html.P(id="popis-vyberu", role="status",
               style={"fontSize": "14px", "color": "#61738a", "margin": "16px 0 0"}),
    ], style={"backgroundColor": "white", "padding": "22px", "borderRadius": "12px",
              "marginBottom": "22px"}),
    html.Div([
        vytvor_kartu("Tržby", "kpi-trzby", "Součet hodnot vybraných objednávek"),
        vytvor_kartu("Počet objednávek", "kpi-pocet", "Počet řádků po použití filtrů"),
        vytvor_kartu("Průměrná objednávka", "kpi-prumer", "Tržby dělené počtem objednávek"),
    ], style=STYL_RADKU),
    html.Div([
        html.Div(dcc.Graph(id="graf-cas", config={"displaylogo": False}),
                 style={"flex": "1 1 460px", "minWidth": 0, "backgroundColor": "white",
                        "borderRadius": "12px", "overflow": "hidden"}),
        html.Div(dcc.Graph(id="graf-region", config={"displaylogo": False}),
                 style={"flex": "1 1 460px", "minWidth": 0, "backgroundColor": "white",
                        "borderRadius": "12px", "overflow": "hidden"}),
    ], style={**STYL_RADKU, "marginTop": "22px"}),
    html.Footer([
        html.P("Jeden řádek představuje jednu objednávku v jedné kategorii. "
               "Všechny karty i grafy používají stejný výběr dat."),
        html.P("Částky v kartách zaokrouhlujeme na celé Kč. Pomlčka znamená, "
               "že průměr pro prázdný výběr neexistuje."),
    ], style={"fontSize": "12px", "color": "#61738a", "marginTop": "18px"}),
], style={"fontFamily": "Arial, sans-serif", "color": TMAVA,
          "backgroundColor": "#f2f5f9", "maxWidth": "1280px",
          "margin": "0 auto", "padding": "24px"})


# 4. Jediné propojení vstupů a všech souvisejících výstupů
# Šest Outputů odpovídá šesti položkám return. Dva Inputy parametrům funkce.
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
             f"Výběr obsahuje {len(vyber)} z {len(df)} objednávek.")
    return (
        vytvor_graf_casu(vyber),     # 1: graf-cas.figure
        vytvor_graf_regionu(vyber),  # 2: graf-region.figure
        trzby,                     # 3: kpi-trzby.children
        pocet,                     # 4: kpi-pocet.children
        prumer,                    # 5: kpi-prumer.children
        popis,                     # 6: popis-vyberu.children
    )


# 5. Spuštění místního serveru; po změně kódu Stop, Run a obnovení stránky.
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
