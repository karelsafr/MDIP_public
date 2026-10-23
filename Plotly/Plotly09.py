"""Plotly09 | Uložení grafu do HTML, PNG a PDF.

Cíl: uložit interaktivní i statickou verzi stejného grafu.
Novinka: write_html a write_image. PNG/PDF vyžadují Kaleido a Chrome.
Zkuste: otevřete HTML a PDF a porovnejte možnosti práce s grafem.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


def vytvor_graf():
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    data = pd.read_csv(cesta)
    regiony = data.groupby("region", as_index=False)["trzba"].sum()
    regiony = regiony.sort_values("trzba", ascending=False)

    fig = px.bar(
        regiony,
        x="region",
        y="trzba",
        labels={"region": "Region", "trzba": "Tržby (Kč)"},
        title="Tržby podle regionu | syntetická data",
        template="plotly_white",
    )
    fig.update_layout(width=1100, height=650, font_size=18, separators=", ")
    fig.update_traces(marker_color="#2563eb")
    fig.update_yaxes(tickformat=",.0f")
    return fig


def uloz_vystupy(fig):
    slozka = Path(__file__).resolve().parents[1] / "vystupy"
    slozka.mkdir(exist_ok=True)

    # JavaScript je uvnitř souboru. HTML pak funguje také bez internetu.
    html = slozka / "Plotly09.html"
    fig.write_html(
        html,
        include_plotlyjs=True,
        full_html=True,
    )
    print(f"HTML: {html}")

    # Tyto dva exporty používají Kaleido a místní Chrome/Chromium.
    png = slozka / "Plotly09.png"
    fig.write_image(png, scale=2)
    print(f"PNG:  {png}")

    pdf = slozka / "Plotly09.pdf"
    fig.write_image(pdf)
    print(f"PDF:  {pdf}")


if __name__ == "__main__":
    graf = vytvor_graf()
    uloz_vystupy(graf)
    graf.show(renderer="browser")
