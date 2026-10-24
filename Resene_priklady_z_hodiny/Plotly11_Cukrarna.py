"""ADMIN - vzorové řešení závěrečného úkolu: kalkulace cukrárny do PDF.

Soubor patří lektorovi. Do studentského ZIPu se neposílá.
Spuštění: Run v PyCharmu; výstupy vzniknou ve složce vystupy vedle skriptu.
Všechny ceny jsou smyšlené výukové údaje. Recept popisuje celou dávku.
Modelový zisk = cena - suroviny - práce - ostatní zadané náklady.
Fixní režii, DPH ani daně model neřeší; nemáme údaje o skutečných prodejích.

Nové kroky proti Plotly10: spojení tří tabulek, přepočet balení na spotřebu
v receptu a kalkulace na jeden kus. Výsledkem zůstává jedna figura Plotly.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

SAZBA_PRACE_KC_H = 240
SLOZKA = Path(__file__).resolve().parent


def format_cislo(hodnota, desetinna_mista=2):
    """Formátujeme až hotový výsledek, nikoli mezivýpočty."""
    return f"{hodnota:,.{desetinna_mista}f}".replace(",", " ").replace(".", ",")


def format_kc(hodnota):
    return format_cislo(hodnota) + " Kč"


def nacti_data():
    """Všechny cesty fungují i při Run z jiného pracovního adresáře."""
    suroviny = pd.read_csv(SLOZKA / "data" / "suroviny.csv")
    recepty = pd.read_csv(SLOZKA / "data" / "recepty.csv")
    polozky = pd.read_csv(SLOZKA / "data" / "polozky_receptu.csv")
    return suroviny, recepty, polozky


def spocitej_kalkulaci(suroviny, recepty, polozky, sazba_prace_kc_h=SAZBA_PRACE_KC_H):
    """Vrátí jeden řádek na recept. Předané tabulky nemění."""
    if recepty.empty:
        raise ValueError("Pro report potřebujeme alespoň jeden recept.")
    if sazba_prace_kc_h < 0:
        raise ValueError("Hodinová sazba práce nesmí být záporná.")
    if (suroviny["velikost_baleni"] <= 0).any() or (recepty["kusu_davka"] <= 0).any():
        raise ValueError("Velikost balení i počet kusů v dávce musí být kladné.")
    if (recepty["prodejni_cena_kc"] <= 0).any():
        raise ValueError("Pro výpočet marže musí být prodejní cena kladná.")

    # 1. K množství v receptu připojíme velikost a cenu balení suroviny.
    # Každá surovina má v ceníku právě jeden řádek: many_to_one tuto vazbu ověří.
    detail = polozky.merge(suroviny, on="surovina_id", how="left", validate="many_to_one")
    if detail[["velikost_baleni", "cena_baleni_kc"]].isna().any().any():
        raise ValueError("Některé položce receptu chybí surovina v ceníku.")
    if not polozky["recept_id"].isin(recepty["recept_id"]).all():
        raise ValueError("Některá položka odkazuje na neznámý recept.")
    # Množství receptu i velikost balení mají stejnou jednotku: g, ml nebo ks.
    detail["naklad_polozky_kc"] = (
        detail["mnozstvi"] / detail["velikost_baleni"] * detail["cena_baleni_kc"]
    )

    # 2. Sečteme suroviny celé dávky a souhrn připojíme k receptům.
    souhrn = detail.groupby("recept_id", as_index=False)["naklad_polozky_kc"].sum()
    souhrn = souhrn.rename(columns={"naklad_polozky_kc": "suroviny_davka_kc"})
    kalkulace = recepty.merge(souhrn, on="recept_id", how="left", validate="one_to_one")
    if kalkulace["suroviny_davka_kc"].isna().any():
        raise ValueError("Některý recept nemá žádné suroviny.")

    # 3. Práce se zadává v minutách za dávku; sazba je v Kč za hodinu.
    kalkulace["prace_davka_kc"] = kalkulace["prace_min_davka"] / 60 * sazba_prace_kc_h
    kalkulace["naklady_davka_kc"] = (
        kalkulace["suroviny_davka_kc"] + kalkulace["prace_davka_kc"]
        + kalkulace["ostatni_naklady_davka_kc"]
    )
    for davka, kus in [
        ("suroviny_davka_kc", "suroviny_ks_kc"),
        ("prace_davka_kc", "prace_ks_kc"),
        ("ostatni_naklady_davka_kc", "ostatni_ks_kc"),
        ("naklady_davka_kc", "naklady_ks_kc"),
    ]:
        kalkulace[kus] = kalkulace[davka] / kalkulace["kusu_davka"]

    # 4. Zisk na kus a procentní marže mají odlišné jednotky.
    kalkulace["zisk_ks_kc"] = kalkulace["prodejni_cena_kc"] - kalkulace["naklady_ks_kc"]
    kalkulace["marze_pct"] = kalkulace["zisk_ks_kc"] / kalkulace["prodejni_cena_kc"] * 100
    return kalkulace


def vytvor_report(kalkulace, sazba_prace_kc_h=SAZBA_PRACE_KC_H):
    """Sestaví dva grafy, tabulku, tři ukazatele a komentář do jedné figury."""
    if kalkulace.empty:
        raise ValueError("PDF report nelze sestavit z prázdné kalkulace.")
    data = kalkulace.sort_values("zisk_ks_kc", ascending=False).copy()
    nejlepsi = data.iloc[0]
    ztratove = data.loc[data["zisk_ks_kc"] < 0]

    # Horní řádek obsahuje dva grafy. Spodní řádek je tabulka přes celou šířku.
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{}, {}], [{"type": "table", "colspan": 2}, None]],
        row_heights=[0.56, 0.44], horizontal_spacing=0.10, vertical_spacing=0.16,
        subplot_titles=("Cena a náklad na kus", "Složení nákladu na kus", "Kalkulace výrobků"),
    )

    # Rozdílné offsetgroup oddělí cenu a náklad do dvou sousedních sloupců.
    # Vpravo jsou všechny složky ve stejné skupině; barmode="stack" je sečte.
    fig.add_trace(go.Bar(
        name="Prodejní cena", y=data["nazev"], x=data["prodejni_cena_kc"],
        orientation="h", offsetgroup="cena", marker_color="#19647e",
        hovertemplate="%{y}<br>Cena: %{x:.2f} Kč/ks<extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        name="Celkový náklad", y=data["nazev"], x=data["naklady_ks_kc"],
        orientation="h", offsetgroup="naklad", marker_color="#a8b1ba",
        hovertemplate="%{y}<br>Náklad: %{x:.2f} Kč/ks<extra></extra>",
    ), row=1, col=1)
    for sloupec, nazev, barva in [
        ("suroviny_ks_kc", "Suroviny", "#c7863a"),
        ("prace_ks_kc", "Práce", "#5f9e8d"),
        ("ostatni_ks_kc", "Ostatní", "#d6dce2"),
    ]:
        fig.add_trace(go.Bar(
            name=nazev, y=data["nazev"], x=data[sloupec], orientation="h",
            offsetgroup="slozeni", marker_color=barva,
            hovertemplate="%{y}<br>" + nazev + ": %{x:.2f} Kč/ks<extra></extra>",
        ), row=1, col=2)

    # Oba grafy mají stejné pořadí výrobků; popisky názvů stačí vlevo.
    for col in (1, 2):
        fig.update_yaxes(categoryorder="array", categoryarray=data["nazev"].tolist(),
                         autorange="reversed", row=1, col=col)
        fig.update_xaxes(title_text="Kč na kus", tickformat=".0f", rangemode="tozero",
                         gridcolor="#e8edf1", row=1, col=col)
    fig.update_yaxes(showticklabels=False, row=1, col=2)

    # Ztrátu zvýrazníme barvou řádku i záporným číslem, nikoli jen barvou.
    barvy_radku = ["#fff0ef" if z < 0 else "#f5f7f9" for z in data["zisk_ks_kc"]]
    fig.add_trace(go.Table(
        columnwidth=[260, 75, 110, 110, 120, 90],
        header=dict(
            values=["<b>Výrobek</b>", "<b>Ks / dávka</b>", "<b>Cena / ks</b>",
                    "<b>Náklad / ks</b>", "<b>Modelový zisk / ks</b>", "<b>Marže</b>"],
            fill_color="#e1e8ee", align=["left", "right", "right", "right", "right", "right"],
            font=dict(size=17, color="#172c3c"), height=42,
        ),
        cells=dict(
            values=[data["nazev"], data["kusu_davka"],
                    [format_kc(v) for v in data["prodejni_cena_kc"]],
                    [format_kc(v) for v in data["naklady_ks_kc"]],
                    [format_kc(v) for v in data["zisk_ks_kc"]],
                    [format_cislo(v, 1) + " %" for v in data["marze_pct"]]],
            fill_color=[barvy_radku] * 6,
            align=["left", "right", "right", "right", "right", "right"],
            font=dict(size=17, color="#172c3c"), height=39,
        ),
    ), row=2, col=1)

    ukazatele = [
        (0.00, "Počet receptů", str(len(data))),
        (0.33, "Nejvyšší modelový zisk / ks", format_kc(nejlepsi["zisk_ks_kc"])),
        (0.75, "Ztrátových výrobků", str(len(ztratove))),
    ]
    for x, popis, hodnota in ukazatele:
        fig.add_annotation(x=x, y=1.10, xref="paper", yref="paper",
                           xanchor="left", yanchor="bottom", align="left", showarrow=False,
                           text=f"{popis}<br><b>{hodnota}</b>", font=dict(size=22))

    if ztratove.empty:
        zaver = "Každý výrobek má za těchto předpokladů nezáporný modelový zisk na kus."
    else:
        nazvy = ", ".join(ztratove["nazev"])
        zaver = f"Ztrátové výrobky: {nazvy}. Jejich cena nepokrývá započtené náklady."
    komentar = (
        f"<b>Výsledek:</b> Nejvyšší modelový zisk na kus má {nejlepsi['nazev']}: "
        f"{format_kc(nejlepsi['zisk_ks_kc'])}.<br>{zaver}"
    )
    fig.add_annotation(x=0, y=-0.035, xref="paper", yref="paper",
                       xanchor="left", yanchor="top", align="left", text=komentar,
                       showarrow=False, font=dict(size=18))
    fig.add_annotation(
        x=0, y=-0.105, xref="paper", yref="paper", xanchor="left", yanchor="top",
        align="left", showarrow=False, font=dict(size=15, color="#4e6272"),
        text=("Modelový zisk = cena − suroviny − práce − ostatní zadané náklady. "
              "Fixní režii, DPH ani daně nepočítáme.<br>"
              "Zdroj: smyšlené výukové ceny a recepty. Bez údajů o prodaném množství "
              "nepočítáme celkový zisk cukrárny."),
    )
    fig.update_layout(
        title=dict(text="<b>Cukrárna: kalkulace výrobků</b><br>"
                        f"<sup>Syntetická data | sazba práce {format_cislo(sazba_prace_kc_h, 0)} Kč/h</sup>",
                   x=0.06, y=0.96, xanchor="left", yanchor="top", font_size=30),
        width=1800, height=1250, template="plotly_white",
        margin=dict(l=245, r=65, t=235, b=170),
        font=dict(family="Arial", size=17, color="#172c3c"),
        barmode="stack", bargap=0.28, bargroupgap=0.12,
        legend=dict(orientation="h", x=0, y=1.045, xanchor="left", yanchor="bottom", font_size=16),
        separators=", ", paper_bgcolor="white", plot_bgcolor="white",
    )
    return fig


def uloz_vystupy(fig):
    """Kaleido + Chrome vykreslí PDF a PNG; HTML je samostatně přenositelné."""
    slozka = SLOZKA / "vystupy"
    slozka.mkdir(exist_ok=True)
    for pripona in ("pdf", "png", "html"):
        cesta = slozka / f"cukrarna_report.{pripona}"
        if pripona == "html":
            fig.write_html(cesta, include_plotlyjs=True, full_html=True)
        else:
            fig.write_image(cesta)
        print(cesta)


if __name__ == "__main__":
    suroviny, recepty, polozky = nacti_data()
    kalkulace = spocitej_kalkulaci(suroviny, recepty, polozky)
    graf = vytvor_report(kalkulace)
    uloz_vystupy(graf)
    graf.show(renderer="browser")
