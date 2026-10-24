"""ADMIN | Dash13: cukrárna se dvěma záložkami. Vyřešený závěrečný úkol.

Určeno lektorovi; tento soubor nepatří do studentského ZIPu.
Spuštění: Run v PyCharmu a http://127.0.0.1:8050/.
Po změně kódu: Stop, Run a obnovení stránky.

Novinky: propojení tří CSV, dcc.Tabs/dcc.Tab a přepočet receptu na dávky.
1. Data a kalkulace, 2. grafy a tabulka, 3. layout, 4. callbacky, 5. server.
Ceny i recepty jsou syntetické výukové údaje. Náklad není nákup celých balení:
počítáme hodnotu spotřebované části balení, práce a ostatních nákladů.
Modelový zisk nezahrnuje fixní režii, DPH ani daně. Není čistým ziskem provozu.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

# 1. Data a výpočty. Jeden recept popisuje jednu dávku několika kusů.
SLOZKA_DAT = Path(__file__).resolve().parent / "data"
SAZBA_PRACE_KC_H = 240
AKCENT = "#88583b"
ZELENA = "#227565"
CERVENA = "#b44444"
INKOUST = "#302a26"
STYL_RADKU = {"display": "flex", "flexWrap": "wrap", "gap": "16px"}
STYL_KARTY = {"backgroundColor": "white", "padding": "18px 20px",
              "border": "1px solid #e7ddd4", "borderRadius": "10px",
              "flex": "1 1 210px", "minWidth": 0}
STYL_PANELU = {"backgroundColor": "white", "padding": "16px",
               "border": "1px solid #e7ddd4", "borderRadius": "10px",
               "flex": "1 1 440px", "minWidth": 0}


def nacti_data():
    """Cesty jsou odvozeny od souboru, nezávisí na pracovním adresáři."""
    suroviny = pd.read_csv(SLOZKA_DAT / "suroviny.csv")
    recepty = pd.read_csv(SLOZKA_DAT / "recepty.csv")
    polozky = pd.read_csv(SLOZKA_DAT / "polozky_receptu.csv")
    return suroviny, recepty, polozky


def spocitej_kalkulaci(suroviny, recepty, polozky):
    """Vrátí přehled výrobků a položky receptů s nákladem na jednu dávku."""
    if (suroviny["velikost_baleni"] <= 0).any() or (recepty["kusu_davka"] <= 0).any():
        raise ValueError("Velikost balení i počet kusů v dávce musí být kladné.")
    if (recepty["prodejni_cena_kc"] <= 0).any():
        raise ValueError("Pro výpočet marže musí být prodejní cena kladná.")

    # Každý řádek položky najde právě jednu surovinu podle jejího id.
    polozky_s_cenou = polozky.merge(suroviny, on="surovina_id", how="left",
                                   validate="many_to_one")
    if polozky_s_cenou["nazev_suroviny"].isna().any():
        raise ValueError("Položka receptu odkazuje na neznámou surovinu.")
    if not polozky["recept_id"].isin(recepty["recept_id"]).all():
        raise ValueError("Položka patří k neznámému receptu.")
    polozky_s_cenou["naklad_suroviny_kc"] = (
        polozky_s_cenou["mnozstvi"] / polozky_s_cenou["velikost_baleni"]
        * polozky_s_cenou["cena_baleni_kc"]
    )
    souhrn = polozky_s_cenou.groupby("recept_id", as_index=False)["naklad_suroviny_kc"].sum()
    souhrn = souhrn.rename(columns={"naklad_suroviny_kc": "suroviny_davka_kc"})
    kalkulace = recepty.merge(souhrn, on="recept_id", how="left", validate="one_to_one")
    if kalkulace["suroviny_davka_kc"].isna().any():
        raise ValueError("Každý recept musí mít alespoň jednu položku suroviny.")

    kalkulace["prace_davka_kc"] = kalkulace["prace_min_davka"] / 60 * SAZBA_PRACE_KC_H
    kalkulace["naklady_davka_kc"] = (
        kalkulace["suroviny_davka_kc"] + kalkulace["prace_davka_kc"]
        + kalkulace["ostatni_naklady_davka_kc"]
    )
    kalkulace["naklady_ks_kc"] = kalkulace["naklady_davka_kc"] / kalkulace["kusu_davka"]
    kalkulace["zisk_ks_kc"] = kalkulace["prodejni_cena_kc"] - kalkulace["naklady_ks_kc"]
    kalkulace["marze_pct"] = kalkulace["zisk_ks_kc"] / kalkulace["prodejni_cena_kc"] * 100
    # Nezaokrouhlujeme mezivýpočty. Formátování patří až do textů a grafů.
    return kalkulace, polozky_s_cenou


suroviny, recepty, polozky = nacti_data()
kalkulace, polozky_s_cenou = spocitej_kalkulaci(suroviny, recepty, polozky)


def format_cislo(hodnota, desetinna_mista=2):
    return f"{hodnota:,.{desetinna_mista}f}".replace(",", " ").replace(".", ",")


def format_kc(hodnota):
    return format_cislo(hodnota) + " Kč"


# 2. Grafy a tabulka. Funkce dostávají již vybraná data.
def uprav_graf(fig, vyska=420):
    fig.update_layout(
        template="plotly_white", font={"family": "Arial", "size": 13, "color": INKOUST},
        height=vyska, margin={"l": 165, "r": 30, "t": 95, "b": 55},
        paper_bgcolor="white", plot_bgcolor="white", separators=", ",
        title={"y": 0.98, "yanchor": "top"},
        legend={"orientation": "h", "y": 1.02, "yanchor": "bottom", "x": 0},
    )
    fig.update_xaxes(gridcolor="#eee6df")
    return fig


def prazdny_graf(nadpis):
    fig = go.Figure()
    fig.add_annotation(text="Pro tento výběr nejsou data.",
                       x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(title=nadpis)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return uprav_graf(fig)


def graf_ceny_a_naklady(data):
    if data.empty:
        return prazdny_graf("Cena a náklad na 1 kus")
    serazene = data.sort_values("prodejni_cena_kc")
    fig = go.Figure()
    fig.add_bar(name="Prodejní cena", y=serazene["nazev"], x=serazene["prodejni_cena_kc"],
                orientation="h", marker_color=AKCENT)
    fig.add_bar(name="Náklad", y=serazene["nazev"], x=serazene["naklady_ks_kc"],
                orientation="h", marker_color="#c5ab95")
    fig.update_traces(hovertemplate="%{y}<br>%{x:,.2f} Kč / kus<extra>%{fullData.name}</extra>")
    fig.update_layout(title="Cena a náklad na 1 kus", barmode="group")
    fig.update_xaxes(title="Kč / kus", rangemode="tozero")
    return uprav_graf(fig)


def graf_zisku(data):
    if data.empty:
        return prazdny_graf("Modelový zisk na 1 kus")
    serazene = data.sort_values("zisk_ks_kc")
    fig = px.bar(serazene, x="zisk_ks_kc", y="nazev", orientation="h",
                 labels={"zisk_ks_kc": "Kč / kus", "nazev": ""},
                 title="Modelový zisk na 1 kus")
    fig.update_traces(
        marker_color=[CERVENA if z < 0 else ZELENA for z in serazene["zisk_ks_kc"]],
        hovertemplate="%{y}<br>Modelový zisk: %{x:,.2f} Kč / kus<extra></extra>",
    )
    fig.add_vline(x=0, line_color="#77695f", line_width=1)
    return uprav_graf(fig)


def graf_surovin(data):
    if data.empty:
        return prazdny_graf("Podíl surovin na nákladu surovin")
    fig = px.pie(data, names="nazev_suroviny", values="naklad_suroviny_kc",
                 hole=0.48, title="Z čeho se skládá náklad surovin",
                 color_discrete_sequence=["#88583b", "#227565", "#b78a63", "#d8b98b",
                                          "#b45b54", "#7f8780", "#647d8c", "#c8c6ad"])
    fig.update_traces(textinfo="percent", textposition="inside",
                      hovertemplate="%{label}<br>%{value:,.2f} Kč (%{percent})<extra></extra>")
    fig.update_layout(template="plotly_white", height=350,
                       margin={"l": 15, "r": 15, "t": 55, "b": 20},
                       font={"family": "Arial", "size": 13, "color": INKOUST},
                       separators=", ", legend={"orientation": "h", "y": -0.06})
    return fig


def tabulka_surovin(data):
    """Obyčejná HTML tabulka; sloupce tabulky řídíme explicitně."""
    styl_bunky = {"padding": "9px 8px", "borderBottom": "1px solid #eee6df", "textAlign": "left"}
    hlavicka = html.Thead(html.Tr([
        html.Th(text, style=styl_bunky) for text in ["Surovina", "Množství", "Jednotka", "Náklad"]
    ]))
    radky = []
    for _, polozka in data.iterrows():
        radky.append(html.Tr([
            html.Td(polozka["nazev_suroviny"], style=styl_bunky),
            html.Td(format_cislo(polozka["mnozstvi"], 0), style=styl_bunky),
            html.Td(polozka["jednotka"], style=styl_bunky),
            html.Td(format_kc(polozka["naklad_suroviny_kc"]), style=styl_bunky),
        ]))
    return html.Table([hlavicka, html.Tbody(radky)],
                      style={"width": "100%", "borderCollapse": "collapse", "fontSize": "14px"})


def vytvor_kartu(nazev, id_hodnoty, vysvetleni):
    return html.Div([
        html.P(nazev, style={"margin": "0 0 8px", "color": "#74675e", "fontSize": "14px"}),
        html.Div(id=id_hodnoty, style={"fontSize": "29px", "fontWeight": "700"}),
        html.P(vysvetleni, style={"margin": "8px 0 0", "fontSize": "12px", "color": "#74675e"}),
    ], style=STYL_KARTY)


# 3. Záložky mají obsah přímo v children. Není nutný callback pro přepínání.
# Všechna id jsou již součástí layoutu. Obě datové aktualizace jsou nezávislé.
app = Dash(__name__)
app.title = "Cukrárna: nabídka a receptář"
app.layout = html.Div([
    html.Header([
        html.H1("Cukrárna: nabídka a receptář", style={"margin": "0 0 9px", "fontSize": "30px"}),
        html.P("Šest výrobků, náklady na výrobu a recepty po dávkách. Syntetická výuková data.",
               style={"margin": 0, "color": "#eaded4"}),
    ], style={"backgroundColor": AKCENT, "color": "white", "padding": "24px",
              "borderRadius": "12px", "marginBottom": "18px"}),
    dcc.Tabs(id="zalozky", value="nabidka", children=[
        dcc.Tab(label="Nabídka a zisk", value="nabidka", children=[
            html.Div([
                html.Label("Kategorie výrobků", htmlFor="kategorie"),
                dcc.Dropdown(id="kategorie", options=["Všechny"] + sorted(kalkulace["kategorie"].unique()),
                             value="Všechny", clearable=False),
                html.P(id="nabidka-popis", role="status", style={"fontSize": "13px", "color": "#74675e"}),
                html.Div([
                    vytvor_kartu("Výrobky ve výběru", "nabidka-pocet", "Počet různých receptů"),
                    vytvor_kartu("Nejvyšší modelový zisk / kus", "nabidka-zisk", "Maximum ve zvoleném výběru"),
                    vytvor_kartu("Ztrátové výrobky", "nabidka-ztratove", "Prodejní cena je nižší než náklad"),
                ], style=STYL_RADKU),
                html.Div([
                    html.Div(dcc.Graph(id="graf-cena-naklad", config={"displaylogo": False}), style=STYL_PANELU),
                    html.Div(dcc.Graph(id="graf-zisk", config={"displaylogo": False}), style=STYL_PANELU),
                ], style={**STYL_RADKU, "marginTop": "16px"}),
            ], style={"paddingTop": "20px"}),
        ]),
        dcc.Tab(label="Receptář", value="receptar", children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.Label("Recept", htmlFor="vybrany-recept"),
                        dcc.Dropdown(id="vybrany-recept", options=[
                            {"label": r["nazev"], "value": r["recept_id"]} for _, r in kalkulace.iterrows()
                        ], value="R01", clearable=False),
                    ], style={"flex": "2 1 280px", "minWidth": 0}),
                    html.Div([
                        html.Label("Počet dávek", htmlFor="pocet-davek"),
                        dcc.Dropdown(id="pocet-davek", options=[
                            {"label": "1 dávka", "value": 1}, {"label": "2 dávky", "value": 2},
                            {"label": "3 dávky", "value": 3},
                        ], value=1, clearable=False),
                    ], style={"flex": "1 1 180px", "minWidth": 0}),
                ], style=STYL_RADKU),
                html.H2(id="recept-nazev", style={"fontSize": "23px", "margin": "18px 0 12px"}),
                html.Div([
                    vytvor_kartu("Vyrobené kusy", "recept-kusy", "Počet kusů v dávce × počet dávek"),
                    vytvor_kartu("Náklad zvolených dávek", "recept-naklady", "Suroviny + práce + ostatní náklady"),
                    vytvor_kartu("Modelový zisk zvolených dávek", "recept-zisk", "Při prodeji všech vyrobených kusů"),
                ], style=STYL_RADKU),
                html.P(id="recept-vysvetleni", role="status", style={"fontSize": "13px", "color": "#74675e", "lineHeight": "1.5"}),
                html.Div([
                    html.Div([
                        html.H3("Suroviny pro zvolené dávky", style={"margin": "0 0 8px", "fontSize": "18px"}),
                        html.Div(id="recept-tabulka", style={"overflowX": "auto"}),
                    ], style=STYL_PANELU),
                    html.Div(dcc.Graph(id="recept-graf", config={"displaylogo": False}), style=STYL_PANELU),
                ], style=STYL_RADKU),
                html.H3("Postup pro jednu dávku", style={"fontSize": "18px", "marginBottom": "8px"}),
                html.P("Pro více dávek postup opakujte. V tomto modelu roste spotřeba, práce i ostatní náklady přímo úměrně počtu dávek.",
                       style={"fontSize": "13px", "color": "#74675e"}),
                html.Ol(id="recept-postup", style={"lineHeight": "1.5", "paddingLeft": "22px", "fontSize": "14px"}),
            ], style={"paddingTop": "20px"}),
        ]),
    ]),
    html.Footer([
        html.P("Modelový zisk = prodejní cena − suroviny − práce − ostatní náklady. "
               "Sazba práce: 240 Kč/h. Fixní režii, DPH ani daně model nezahrnuje."),
        html.P("Ceny jsou smyšlené; nejde o ceník ani skutečný zisk provozu. "
               "Recepty jsou zjednodušené výukové záznamy, bez údajů o skutečných prodejích."),
    ], style={"fontSize": "12px", "color": "#74675e", "marginTop": "18px", "lineHeight": "1.4"}),
], style={"fontFamily": "Arial, sans-serif", "color": INKOUST, "backgroundColor": "#f7f3ee",
          "maxWidth": "1280px", "margin": "0 auto", "padding": "24px", "boxSizing": "border-box"})


# 4a. První záložka: všechny výstupy používají stejný výběr kategorií.
@app.callback(
    Output("nabidka-pocet", "children"),
    Output("nabidka-zisk", "children"),
    Output("nabidka-ztratove", "children"),
    Output("graf-cena-naklad", "figure"),
    Output("graf-zisk", "figure"),
    Output("nabidka-popis", "children"),
    Input("kategorie", "value"),
)
def aktualizuj_nabidku(kategorie):
    if kategorie == "Všechny":
        vyber = kalkulace
    else:
        vyber = kalkulace.loc[kalkulace["kategorie"] == kategorie]
    nejvyssi_zisk = "—" if vyber.empty else format_kc(vyber["zisk_ks_kc"].max())
    return (
        str(len(vyber)), nejvyssi_zisk, str((vyber["zisk_ks_kc"] < 0).sum()),
        graf_ceny_a_naklady(vyber), graf_zisku(vyber),
        f"Kategorie: {kategorie}. Zobrazeno {len(vyber)} z {len(kalkulace)} výrobků. Částky jsou za 1 kus.",
    )


# 4b. Druhá záložka: změna receptu i počtu dávek aktualizuje celý receptář.
@app.callback(
    Output("recept-nazev", "children"),
    Output("recept-kusy", "children"),
    Output("recept-naklady", "children"),
    Output("recept-zisk", "children"),
    Output("recept-tabulka", "children"),
    Output("recept-postup", "children"),
    Output("recept-graf", "figure"),
    Output("recept-vysvetleni", "children"),
    Input("vybrany-recept", "value"),
    Input("pocet-davek", "value"),
)
def aktualizuj_recept(recept_id, pocet_davek):
    vyber = kalkulace.loc[kalkulace["recept_id"] == recept_id]
    if vyber.empty or pocet_davek not in (1, 2, 3):
        return ("Vyberte recept a počet dávek.", "—", "—", "—", [], [],
                prazdny_graf("Suroviny"), "Chybí platný výběr.")
    recept = vyber.iloc[0]
    # .copy(): násobíme lokální výběr, původní údaje jedné dávky zůstávají stejné.
    suroviny_davek = polozky_s_cenou.loc[polozky_s_cenou["recept_id"] == recept_id].copy()
    suroviny_davek["mnozstvi"] *= pocet_davek
    suroviny_davek["naklad_suroviny_kc"] *= pocet_davek
    kusy = int(recept["kusu_davka"] * pocet_davek)
    naklad = recept["naklady_davka_kc"] * pocet_davek
    trzba = recept["prodejni_cena_kc"] * kusy
    modelovy_zisk = trzba - naklad
    vysvetleni = (
        f"Suroviny: {format_kc(recept['suroviny_davka_kc'] * pocet_davek)}; "
        f"práce: {format_kc(recept['prace_davka_kc'] * pocet_davek)}; "
        f"ostatní: {format_kc(recept['ostatni_naklady_davka_kc'] * pocet_davek)}. "
        f"Prodejní cena: {format_kc(recept['prodejni_cena_kc'])} / kus. "
        f"Modelová marže: {format_cislo(recept['marze_pct'], 1)} %."
    )
    if recept_id == "R05":
        vysvetleni += " Vejce účtujeme celá; využití zbylých žloutků model neodečítá."
    return (
        recept["nazev"], str(kusy), format_kc(naklad), format_kc(modelovy_zisk),
        tabulka_surovin(suroviny_davek),
        [html.Li(krok.strip()) for krok in recept["postup"].split("|")],
        graf_surovin(suroviny_davek), vysvetleni,
    )


# 5. Místní výukový server; před spuštěním jiného příkladu použijte Stop.
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
