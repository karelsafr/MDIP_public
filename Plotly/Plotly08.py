"""Plotly08 | Rozvržení přehledové stránky.

Cíl: vyhradit místo pro časový graf, sloupce a krátký text.
Novinka: colspan, row_heights, prázdný panel a okraje celé stránky.
Zkuste: upravte poměr výšek řádků a text v pravé dolní části.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots


def vytvor_graf():
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    data = pd.read_csv(cesta, parse_dates=["datum"])
    denne = data.groupby("datum", as_index=False)["trzba"].sum().sort_values("datum")
    regiony = data.groupby("region", as_index=False)["trzba"].sum()
    regiony = regiony.sort_values("trzba", ascending=False)

    # Mřížka má 2 řádky a 2 sloupce. Každý vnitřní seznam popisuje jeden řádek.
    # {} vytvoří běžný panel; colspan=2 spojí dva sloupce.
    # None nahoře patří spojenému panelu, None dole ponechá místo bez os.
    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[
            [{"colspan": 2}, None],
            [{}, None],
        ],
        row_heights=[0.55, 0.45],
        vertical_spacing=0.21,
        horizontal_spacing=0.14,
        subplot_titles=("Denní tržby", "Tržby podle regionu"),
    )
    for serie in px.line(denne, x="datum", y="trzba").data:
        fig.add_trace(serie, row=1, col=1)
    for serie in px.bar(regiony, x="region", y="trzba").data:
        fig.add_trace(serie, row=2, col=1)

    # Prázdný pravý dolní prostor slouží textu, takže nemá vlastní osy.
    # paper: (0, 0) je levý dolní roh vykreslovací plochy bez okrajů, (1, 1) pravý horní.
    # xanchor/yanchor určí, kterou hranou textu se zadané polohy dotýkáme.
    # <br> přidá nový řádek a <b>...</b> zvýrazní krátkou část textu.
    fig.add_annotation(
        x=0.59,
        y=0.30,
        xref="paper",
        yref="paper",
        xanchor="left",
        yanchor="top",
        align="left",
        showarrow=False,
        text=(
            "<b>Jak číst tento přehled</b><br><br>"
            "Horní graf ukazuje vývoj po dnech.<br>"
            "Dolní graf porovnává regiony.<br><br>"
            "Každý řádek vstupu je jedna objednávka.<br>"
            "Zdroj: syntetická data pro workshop."
        ),
        font={"size": 19},
    )
    fig.update_xaxes(title_text="Datum", row=1, col=1)
    fig.update_xaxes(title_text="Region", row=2, col=1)
    fig.update_yaxes(title_text="Tržby (Kč)", tickformat=",.0f")
    # width/height určují celou figuru; margin rezervuje okraje l/r/t/b v pixelech.
    fig.update_layout(
        title="Rozvržení přehledu objednávek",
        template="plotly_white",
        width=1400,
        height=950,
        margin={"l": 95, "r": 55, "t": 110, "b": 85},
        font={"family": "Arial", "size": 17},
        showlegend=False,
        separators=", ",
    )
    return fig


if __name__ == "__main__":
    graf = vytvor_graf()
    graf.show(renderer="browser")
