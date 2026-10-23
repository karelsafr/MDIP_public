"""Dash07: první callback.

Cíl: po změně výběru aktualizovat text na stránce.
Novinka: Input, Output a funkce označená @app.callback.
Zkusit: změň větu vrácenou funkcí zobraz_vyber().
Spuštění: Run, http://127.0.0.1:8050. Před dalším příkladem Stop.
"""

from pathlib import Path

import pandas as pd
from dash import Dash, Input, Output, dcc, html

SOUBOR_DAT = Path(__file__).resolve().parents[1] / "data" / "objednavky.csv"
df = pd.read_csv(SOUBOR_DAT, parse_dates=["datum"])
regiony = ["Všechny"] + sorted(df["region"].unique())

app = Dash(__name__)
app.title = "Dash07: první callback"
app.layout = html.Div([
    html.H1("Výběr regionu"),
    html.Label("Region", htmlFor="region"),
    dcc.Dropdown(id="region", options=regiony, value="Všechny", clearable=False),
    html.P(id="popis-vyberu"),
], style={"maxWidth": "600px", "margin": "40px auto",
          "fontFamily": "Arial, sans-serif"})


# Dekorátor registruje propojení. Obě id musí existovat v app.layout výše.
# Z region.value přichází řetězec; návrat funkce nahradí popis-vyberu.children.
@app.callback(
    Output("popis-vyberu", "children"),
    Input("region", "value"),
)
def zobraz_vyber(region):
    # region je hodnota Inputu, nikoli automatický odkaz na komponentu.
    # Dash funkci zavolá při načtení stránky i po změně výběru. Nevoláme ji ručně.
    if region == "Všechny":
        return "Vybrané regiony: všechny."
    return f"Vybraný region: {region}."


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
