"""Dash02: nadpis a text.

Cíl: popsat obsah stránky pomocí komponent.
Novinka: html.H1, html.P a seznam potomků v html.Div.
Zkusit: přidej další odstavec s vlastní otázkou k datům.
Spuštění: Run, http://127.0.0.1:8050. Před dalším příkladem Stop.
"""

from dash import Dash, html

app = Dash(__name__)
app.title = "Dash02: text na stránce"
# Strom komponent: Div obsahuje jeden nadpis a dva odstavce.
# children je obsah komponenty. U H1 a P předáváme tentýž obsah prvním argumentem.
app.layout = html.Div(children=[
    html.H1("Přehled objednávek"),
    html.P(
        "Jak se vyvíjejí tržby a jaké "
        "rozdíly vidíme mezi regiony?"
    ),
    html.P("Pracujeme se syntetickými daty vytvořenými pro workshop."),
])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
