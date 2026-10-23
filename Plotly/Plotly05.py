"""Plotly05 | Čitelnost a vzhled grafu.

Cíl: upravit hotový graf pro konkrétního čtenáře.
Novinka: update_layout, update_traces, formát os a hovertemplate.
Zkuste: změňte barvu sloupců a doplňte do nadpisu sledované období.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px


def vytvor_graf():
    cesta = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
    data = pd.read_csv(cesta)
    souhrn = data.groupby("region", as_index=False)["trzba"].sum()
    souhrn = souhrn.sort_values("trzba", ascending=False)

    fig = px.bar(souhrn, x="region", y="trzba", text="trzba")
    # Celá figura: nadpis, motiv, písmo a velikost pracovní plochy.
    fig.update_layout(
        title="Tržby podle regionu | syntetická data",
        template="plotly_white",
        font={"family": "Arial", "size": 17},
        separators=", ",  # Desetinná čárka a mezera mezi tisíci.
        width=1100,
        height=650,
    )
    # Datová série: vzhled sloupců, text nad sloupcem a obsah při najetí myší.
    fig.update_traces(
        marker_color="#2563eb",
        texttemplate="%{y:,.0f} Kč",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Tržby: %{y:,.0f} Kč<extra></extra>",
    )
    # Osy: názvy, formát značek a rozsah. Rezerva nahoře chrání text nad sloupci.
    fig.update_xaxes(title_text="Region")
    fig.update_yaxes(
        title_text="Tržby (Kč)",
        tickformat=",.0f",
        range=[0, souhrn["trzba"].max() * 1.18],
    )
    return fig


if __name__ == "__main__":
    graf = vytvor_graf()
    graf.show(renderer="browser")
