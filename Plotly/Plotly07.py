"""Plotly07 | Dva grafy v jedné figuře.

Cíl: vytvořit společný výstup pro dva různé pohledy na data.
Novinka: make_subplots a vložení datových sérií do konkrétního panelu.
Zkuste: prohoďte grafy. Změňte také jejich titulky a popisky os.
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

    casovy_graf = px.line(denne, x="datum", y="trzba")
    regionalni_graf = px.bar(regiony, x="region", y="trzba")
    # Jedna společná figura má jeden řádek a dva sloupce.
    # row a col se číslují od 1: levý panel je (1, 1), pravý je (1, 2).
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Denní tržby", "Tržby podle regionu"),
        horizontal_spacing=0.13,
    )

    # Figure.data obsahuje datové série (trace), nikoli celou původní figuru.
    # Série si nese hodnoty a styl. Titulky a osy nastavíme nové figuře zvlášť.
    for serie in casovy_graf.data:
        fig.add_trace(serie, row=1, col=1)
    for serie in regionalni_graf.data:
        fig.add_trace(serie, row=1, col=2)

    fig.update_xaxes(title_text="Datum", row=1, col=1)
    fig.update_xaxes(title_text="Region", row=1, col=2)
    fig.update_yaxes(title_text="Tržby (Kč)", tickformat=",.0f")
    fig.update_layout(
        title="Dva pohledy na stejné objednávky | syntetická data",
        template="plotly_white",
        width=1300,
        height=600,
        font_size=16,
        showlegend=False,
        separators=", ",
    )
    return fig


if __name__ == "__main__":
    graf = vytvor_graf()
    graf.show(renderer="browser")
