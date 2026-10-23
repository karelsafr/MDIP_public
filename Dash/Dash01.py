"""Dash01: první spuštění aplikace.

Cíl: spustit server a otevřít prázdnou stránku v prohlížeči.
Novinka: Dash, app.layout a app.run().
Zkusit: změň html.Div() na html.Div("Ahoj, Dash!").
Spuštění: Run v PyCharmu, potom otevři http://127.0.0.1:8050.
Před dalším příkladem zastav server červeným tlačítkem Stop.
"""

from dash import Dash, html

app = Dash(__name__)
app.title = "Dash01: první aplikace"
# app.layout popisuje obsah webové stránky. Prázdný Div zobrazí prázdnou stránku.
app.layout = html.Div()

if __name__ == "__main__":
    # Python běží jako místní server a prohlížeč se připojí na 127.0.0.1:8050.
    # Zavření karty server nezastaví: použijte Stop v PyCharmu.
    # use_reloader=False: po změně kódu proveďte Stop, Run a obnovte stránku.
    app.run(debug=True, use_reloader=False)
