"""Plotly10 | Hotový jednostránkový PDF dashboard.

Cíl: spojit grafy, souhrnná čísla a krátký komentář do jednoho výstupu.
Novinka: ucelené použití postupů z příkladů Plotly01 až Plotly09.
Funkce vytvor_graf dostane data a vrátí figuru. Tento princip využije i Dash.
Zkuste: vyfiltrujte jeden region a upravte nadpis podle vybraných dat.

Celý obsah i rozvržení tvoří Plotly. Kaleido a Chrome zajišťují export.
Mapa funkce vytvor_graf: 1 data, 2 mřížka, 3 grafy, 4 ukazatele,
5 komentář a zdroj, 6 nadpis a okraje. Potom uloz_vystupy provede export.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots


def format_kc(hodnota):
    """Český zápis korun pro textové části reportu."""
    return f"{hodnota:,.0f}".replace(",", " ") + " Kč"


def nacti_data():
    """Načtení souboru oddělujeme od samotné tvorby grafu."""
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    return pd.read_csv(cesta, parse_dates=["datum"])


def vytvor_graf(data):
    """Z přijatých objednávek vytvoří celý dashboard bez načítání souboru."""
    # 1. Data a souhrny. Funkce očekává sloupce přiloženého CSV a neprázdná data.
    # Prázdný filtr nemá maximum ani nejúspěšnější region, proto ho zastavíme včas.
    if data.empty:
        raise ValueError("PDF dashboard nelze vytvořit: výběr neobsahuje žádné objednávky.")

    denne = data.groupby("datum", as_index=False)["trzba"].sum()
    denne = denne.sort_values("datum")
    regiony = data.groupby("region", as_index=False)["trzba"].sum()
    regiony = regiony.sort_values("trzba", ascending=False)
    celkove_trzby = data["trzba"].sum()
    pocet_objednavek = len(data)
    prumerna_objednavka = celkove_trzby / pocet_objednavek

    # 2. Mřížka: časová řada přes celou šířku; pod ní regiony a histogram.
    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{"colspan": 2}, None], [{}, {}]],
        row_heights=[0.52, 0.48],
        vertical_spacing=0.22,
        horizontal_spacing=0.13,
        subplot_titles=(
            "Denní tržby",
            "Tržby podle regionu",
            "Rozdělení hodnot objednávek",
        ),
    )

    # 3. Grafy: každý nejprve vytvoříme a pak vložíme jeho série do mřížky.
    casovy_graf = px.line(denne, x="datum", y="trzba")
    casovy_graf.update_traces(
        line={"color": "#2563eb", "width": 2.5},
        hovertemplate="%{x|%d.%m.%Y}<br>Tržby: %{y:,.0f} Kč<extra></extra>",
    )
    regionalni_graf = px.bar(regiony, x="region", y="trzba")
    regionalni_graf.update_traces(
        marker_color="#2563eb",
        hovertemplate="%{x}<br>Tržby: %{y:,.0f} Kč<extra></extra>",
    )
    histogram = px.histogram(data, x="trzba", nbins=25)
    histogram.update_traces(marker_color="#0f766e")

    for serie in casovy_graf.data:
        fig.add_trace(serie, row=1, col=1)
    for serie in regionalni_graf.data:
        fig.add_trace(serie, row=2, col=1)
    for serie in histogram.data:
        fig.add_trace(serie, row=2, col=2)

    fig.update_xaxes(title_text="Datum", tickformat="%d.%m.", row=1, col=1)
    fig.update_yaxes(title_text="Tržby (Kč)", tickformat=",.0f", row=1, col=1)
    fig.update_xaxes(title_text="Region", row=2, col=1)
    fig.update_yaxes(title_text="Tržby (Kč)", tickformat=",.0f", row=2, col=1)
    fig.update_xaxes(title_text="Hodnota objednávky (Kč)", tickformat=",.0f", row=2, col=2)
    fig.update_yaxes(title_text="Počet objednávek", row=2, col=2)

    # 4. Ukazatele: vypočtená čísla zformátujeme až při jejich zobrazení.
    # Každý ukazatel je textová anotace nad vykreslovací plochou (y > 1).
    ukazatele = [
        (0.0, "Celkové tržby", format_kc(celkove_trzby)),
        (0.36, "Počet objednávek", f"{pocet_objednavek:,}".replace(",", " ")),
        (0.72, "Průměrná objednávka", format_kc(prumerna_objednavka)),
    ]
    for x, popisek, hodnota in ukazatele:
        fig.add_annotation(
            x=x, y=1.08, xref="paper", yref="paper",
            xanchor="left", yanchor="bottom", align="left",
            text=f"{popisek}<br><b>{hodnota}</b>",
            showarrow=False, font={"size": 22, "color": "#0f172a"},
        )

    # 5. Komentář a zdroj: text se dopočítá ze stejných dat jako grafy a ukazatele.
    # Regiony jsou seřazené sestupně, proto je první řádek region s nejvyšší tržbou.
    nej_region = regiony.iloc[0]
    podil = nej_region["trzba"] / celkove_trzby * 100
    podil_text = f"{podil:.1f}".replace(".", ",")
    nej_den = denne.loc[denne["trzba"].idxmax()]
    komentar = (
        f"<b>Co ukazují data:</b> Nejvyšší tržby má region {nej_region['region']} "
        f"({podil_text} % celku).<br>"
        f"Nejvyšší denní součet připadá na {nej_den['datum']:%d.%m.%Y}: "
        f"{format_kc(nej_den['trzba'])}. Grafy popisují pouze tento ukázkový soubor."
    )
    fig.add_annotation(
        x=0, y=-0.08, xref="paper", yref="paper",
        xanchor="left", yanchor="top", align="left",
        text=komentar, showarrow=False, font={"size": 18},
    )
    fig.add_annotation(
        x=0, y=-0.17, xref="paper", yref="paper",
        xanchor="left", yanchor="top",
        text="Zdroj: syntetická data pro workshop. Jeden řádek = jedna objednávka v jedné kategorii.",
        showarrow=False, font={"size": 15, "color": "#64748b"},
    )

    # 6. Nadpis a okraje: t/b rezervují místo ukazatelům nahoře a komentáři dole.
    # paper souřadnice textu se vztahují k ploše bez těchto okrajů.
    obdobi = f"{data['datum'].min():%d.%m.%Y} až {data['datum'].max():%d.%m.%Y}"
    fig.update_layout(
        title={
            "text": f"<b>Přehled objednávek</b><br><sup>{obdobi}</sup>",
            "x": 0.06, "y": 0.95, "xanchor": "left", "yanchor": "top",
            "font": {"size": 30},
        },
        template="plotly_white",
        width=1600,
        height=1000,
        margin={"l": 95, "r": 50, "t": 205, "b": 155},
        font={"family": "Arial", "size": 17, "color": "#0f172a"},
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        separators=", ",
        bargap=0.18,
    )
    return fig


def uloz_vystupy(fig):
    """Hotovou figuru předáme stejným exportům jako v Plotly09."""
    slozka = Path(__file__).resolve().parents[1] / "vystupy"
    slozka.mkdir(exist_ok=True)
    html = slozka / "dashboard.html"
    fig.write_html(html, include_plotlyjs=True, full_html=True)
    print(f"HTML: {html}")

    pdf = slozka / "dashboard.pdf"
    fig.write_image(pdf)
    print(f"PDF:  {pdf}")

    png = slozka / "dashboard.png"
    fig.write_image(png, scale=1.5)
    print(f"PNG:  {png}")


if __name__ == "__main__":
    data = nacti_data()
    graf = vytvor_graf(data)
    uloz_vystupy(graf)
    graf.show(renderer="browser")
