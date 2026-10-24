"""Průběžné ověření Plotly | řešení pouze pro lektora.

Jeden graf porovnává tržby kategorií ve čtyřech regionech. Ukazuje také
počet objednávek v popisku při najetí myší a souhrn za všechna data.

Spuštění v PyCharmu: Run 'Plotly_Pru01'. Data jsou ve složce data
vedle tohoto skriptu; nezáleží na pracovním adresáři PyCharmu.

Dokumentace k novým prvkům:
https://plotly.com/python/bar-charts/
https://plotly.com/python/hover-text-and-formatting/
https://plotly.com/python/horizontal-vertical-shapes/
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


PORADI_REGIONU = ["Praha", "Brno", "Ostrava", "Plzeň"]
PORADI_KATEGORII = ["Elektronika", "Sport", "Domácnost", "Knihy"]


def nacti_data(cesta=None):
    """Načte objednávky; každý řádek představuje jednu objednávku."""
    if cesta is None:
        cesta = Path(__file__).resolve().parent / "data" / "objednavky.csv"
    return pd.read_csv(cesta, parse_dates=["datum"])


def vytvor_graf(data):
    """Vrátí objekt grafu se čtyřmi datovými sériemi, po jedné na kategorii."""
    if data.empty:
        raise ValueError("Pro toto cvičení potřebujeme neprázdnou tabulku objednávek.")

    # px.bar nekalkuluje součty: tabulku nejprve shrneme podle obou sloupců.
    # size počítá řádky ve skupině; v našich datech jde o počet objednávek.
    souhrn = data.groupby(["region", "kategorie"], as_index=False).agg(
        trzba=("trzba", "sum"),
        pocet=("objednavka_id", "size"),
    )

    # Plzeň / Elektronika v datech nemá objednávky. Souhrn proto obsahuje
    # jen 15 kombinací a na tomto místě nevznikne sloupec. V tomto úplném
    # seznamu objednávek absence kombinace znamená nula objednávek.
    fig = px.bar(
        souhrn,
        x="region",
        y="trzba",
        color="kategorie",
        barmode="group",  # Sloupce kategorií jsou vedle sebe, nikoli nad sebou.
        category_orders={"region": PORADI_REGIONU, "kategorie": PORADI_KATEGORII},
        custom_data=["pocet"],
        labels={"region": "Region", "trzba": "Tržby (Kč)", "kategorie": "Kategorie"},
        title="Tržby podle regionu a kategorie | syntetická data",
        template="plotly_white",
    )

    # custom_data je parametr Plotly Express. V šabloně popisku se používá
    # customdata bez podtržítka; index 0 označuje první předaný sloupec.
    # text za <extra> se zobrazuje v oddělené části popisku (zde kategorie).
    fig.update_traces(
        hovertemplate=(
            "Region: %{x}<br>"
            "Tržby: %{y:,.0f} Kč<br>"
            "Počet objednávek: %{customdata[0]:.0f}"
            "<extra>%{fullData.name}</extra>"
        ),
    )

    # Jde pouze o zvolenou srovnávací hranici. Není to skutečný obchodní
    # cíl ani výsledek výpočtu z dat. add_hline přidá tvar, nikoli další sérii.
    fig.add_hline(
        y=100_000,
        line_dash="dash",
        line_color="#555555",
        annotation_text="Srovnávací hranice 100 000 Kč",
        annotation_position="top right",
        annotation_bgcolor="white",
        annotation_font_size=12,
    )

    celkem = f"{data['trzba'].sum():,.0f}".replace(",", " ")
    fig.add_annotation(
        x=0,
        y=-0.25,
        xref="paper",
        yref="paper",
        xanchor="left",
        yanchor="top",
        text=f"Celkové tržby: <b>{celkem} Kč</b> | {len(data)} objednávek",
        showarrow=False,
        font_size=16,
    )
    fig.update_layout(
        width=1100,
        height=700,
        font_size=15,
        separators=", ",  # Desetinná čárka, mezera mezi tisíci.
        margin=dict(l=90, r=40, t=140, b=150),
        legend=dict(orientation="h", y=1.15, x=0, title_text="Kategorie"),
    )
    fig.update_yaxes(tickformat=",.0f", rangemode="tozero")
    return fig


if __name__ == "__main__":
    graf = vytvor_graf(nacti_data())
    graf.show(renderer="browser")
