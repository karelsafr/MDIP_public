"""Plotly06 | Text a anotace.

Cíl: doplnit graf o konkrétní vysvětlení.
Novinka: anotace v souřadnicích dat a text vůči vykreslovací ploše.
Zkuste: místo maxima označte den s nejnižšími tržbami.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


def vytvor_graf():
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    data = pd.read_csv(cesta, parse_dates=["datum"])
    denne = data.groupby("datum", as_index=False)["trzba"].sum()
    denne = denne.sort_values("datum")
    maximum = denne.loc[denne["trzba"].idxmax()]

    fig = px.line(
        denne,
        x="datum",
        y="trzba",
        labels={"datum": "Datum", "trzba": "Denní tržby (Kč)"},
        title="Nejvyšší denní tržby | syntetická data",
        template="plotly_white",
    )
    # První anotace: x je datum, y je tržba. Šipka ukazuje na konkrétní bod.
    fig.add_annotation(
        x=maximum["datum"],
        y=maximum["trzba"],
        xref="x",
        yref="y",
        text=f"Maximum: {maximum['datum']:%d.%m.%Y}",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-45,
        bgcolor="white",
    )
    # Druhá anotace: paper měří polohu vůči vykreslovací ploše bez okrajů.
    # x: 0 vlevo, 1 vpravo; y: 0 dole, 1 nahoře. Záporné y je pod grafem.
    fig.add_annotation(
        x=0,
        y=-0.27,
        xref="paper",
        yref="paper",
        xanchor="left",
        text="Každý bod je součet tržeb všech objednávek v jednom dni.",
        showarrow=False,
    )
    # Spodní okraj (b = bottom) poskytne místo textu umístěnému pod grafem.
    fig.update_layout(width=1100, height=650, margin={"b": 140}, font_size=16)
    fig.update_yaxes(range=[0, maximum["trzba"] * 1.25])
    return fig


if __name__ == "__main__":
    graf = vytvor_graf()
    graf.show(renderer="browser")
