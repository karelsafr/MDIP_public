"""Plotly02 | Graf nad daty ze souboru.

Cíl: zobrazit součet tržeb pro každý region.
Novinka: načtení CSV a seskupení řádků pomocí groupby.
Zkuste: nahraďte region sloupcem kategorie, včetně popisků grafu.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


def vytvor_graf():
    # Cesta funguje nezávisle na pracovním adresáři v PyCharmu.
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    # read_csv vrací DataFrame: tabulku s řádky a pojmenovanými sloupci.
    data = pd.read_csv(cesta)

    # Jeden řádek CSV = jedna objednávka. Graf potřebuje součty za regiony.
    # groupby spojí stejné regiony, ["trzba"] vybere sčítaný sloupec.
    # as_index=False ponechá region jako běžný sloupec výsledné tabulky.
    souhrn = data.groupby(
        "region", as_index=False
    )["trzba"].sum()
    # Prvním argumentem je tabulka; x a y nyní označují názvy jejích sloupců.
    fig = px.bar(
        souhrn,
        x="region",
        y="trzba",
        labels={"region": "Region", "trzba": "Tržby (Kč)"},
        title="Tržby podle regionu | syntetická data",
    )
    return fig


if __name__ == "__main__":
    graf = vytvor_graf()
    graf.show(renderer="browser")
