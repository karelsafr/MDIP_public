"""Dash06: rozbalovací seznam.

Cíl: vložit ovládací prvek a nastavit jeho možné hodnoty.
Novinka: dcc.Dropdown, options, value, id a clearable.
Zkusit: změň počáteční value na "Praha".
Zde ovladač zatím nemění žádnou jinou komponentu. Propojení přidá Dash07.
Spuštění: Run, http://127.0.0.1:8050. Před dalším příkladem Stop.
"""

from pathlib import Path

import pandas as pd
from dash import Dash, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])
regiony = ["Všechny"] + sorted(df["region"].unique())

# options určuje nabídku, value vybranou hodnotu a id identifikuje komponentu.
# "Všechny" je naše vlastní pomocná volba, nikoli region ve vstupním CSV.
# clearable=False zabrání zrušení výběru na prázdnou hodnotu.
app = Dash(__name__)
app.title = "Dash06: první ovladač"
app.layout = html.Div([
    html.H1("Výběr regionu"),
    html.Label("Region", htmlFor="region"),
    dcc.Dropdown(
        id="region",
        options=regiony,
        value="Všechny",
        clearable=False,
    ),
    html.P("Ovladač zatím není propojený s textem ani s grafy."),
], style={"maxWidth": "600px", "margin": "40px auto",
          "fontFamily": "Arial, sans-serif"})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
