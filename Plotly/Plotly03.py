"""Plotly03 | Vývoj tržeb v čase.

Cíl: zobrazit celkové tržby v jednotlivých dnech.
Novinka: datum jako datum, denní agregace a spojnicový graf.
Zkuste: před agregací vyfiltrujte pouze region Praha.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


def vytvor_graf():
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    # parse_dates načte datum jako časovou hodnotu, nikoli obyčejný text.
    data = pd.read_csv(cesta, parse_dates=["datum"])
    # Po agregaci jeden řádek znamená jeden den, nikoli jednu objednávku.
    denne = data.groupby("datum", as_index=False)["trzba"].sum()
    # Spojnice vede mezi body v pořadí řádků, proto data řadíme.
    denne = denne.sort_values("datum")

    fig = px.line(
        denne,
        x="datum",
        y="trzba",
        labels={"datum": "Datum", "trzba": "Denní tržby (Kč)"},
        title="Denní tržby | syntetická data",
    )
    return fig


if __name__ == "__main__":
    graf = vytvor_graf()
    graf.show(renderer="browser")
