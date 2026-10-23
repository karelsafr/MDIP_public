"""Plotly04 | Histogram hodnot objednávek.

Cíl: zjistit, které hodnoty objednávek jsou v datech obvyklé.
Novinka: histogram sčítá počet pozorování v intervalech hodnot.
Zkuste: změňte nbins z 25 na 10 a porovnejte čitelnost grafu.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


def vytvor_graf():
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    data = pd.read_csv(cesta)

    # Vstupem jsou jednotlivé objednávky, nikoli součty za regiony.
    # nbins je požadavek na přibližný počet intervalů.
    fig = px.histogram(
        data,
        x="trzba",
        nbins=25,
        labels={"trzba": "Hodnota objednávky (Kč)"},
        title="Rozdělení hodnot objednávek | syntetická data",
    )
    fig.update_yaxes(title_text="Počet objednávek")
    return fig


if __name__ == "__main__":
    graf = vytvor_graf()
    graf.show(renderer="browser")
