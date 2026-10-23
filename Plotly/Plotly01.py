"""Plotly01 | První sloupcový graf.

Cíl: spustit krátký skript a prohlédnout si interaktivní graf.
Novinka: Plotly Express vytvoří celý graf jedním voláním.
Zkuste: přidejte čtvrtou kategorii a odpovídající hodnotu.
"""

import plotly.express as px


def vytvor_graf():
    # 1. Seznamy mají stejnou délku. Název a částka na stejné pozici patří k sobě.
    kategorie = ["Knihy", "Sport", "Domácnost"]
    trzby = [12_000, 18_000, 15_000]

    # 2. x a y zde dostávají přímo seznamy hodnot.
    fig = px.bar(
        x=kategorie,
        y=trzby,
        labels={"x": "Kategorie", "y": "Tržby (Kč)"},
        title="Tržby ve třech kategoriích | ukázkové hodnoty",
    )
    # 3. Funkce vrací figuru; sama ještě neotvírá prohlížeč.
    return fig


if __name__ == "__main__":
    # 4. Nejdříve figuru získáme, potom ji zobrazíme.
    graf = vytvor_graf()
    graf.show()
    # nebo:
    # graf.show(renderer="browser")
