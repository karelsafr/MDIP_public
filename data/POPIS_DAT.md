# Objednávky: společná data pro workshop

Jde o **syntetická výuková data**, nikoli skutečné zákazníky nebo výsledky firmy.
Jeden řádek představuje jednu dokončenou objednávku zařazenou do jedné kategorie.
V této zjednodušené tabulce nejsou jednotlivé položky objednávek.

| Sloupec | Význam | Typ |
|---|---|---|
| `objednavka_id` | Jedinečný identifikátor objednávky | text |
| `datum` | Datum objednávky, zápis RRRR-MM-DD | datum po `parse_dates` |
| `region` | Praha, Brno, Ostrava nebo Plzeň | kategorie |
| `kategorie` | Knihy, Domácnost, Sport nebo Elektronika | kategorie |
| `trzba` | Hodnota celé objednávky v Kč | kladné celé číslo |

## Kontrolní hodnoty

- 720 objednávek v období **1. 1. 2025 až 29. 6. 2025**.
- 180 kalendářních dnů, vždy čtyři objednávky za den.
- Celkové tržby **1 878 400 Kč**.
- Průměrná objednávka **2 608,888… Kč**, při zobrazení na celé koruny **2 609 Kč**.
- Praha: 261 objednávek, Brno: 211, Ostrava: 125, Plzeň: 123.
- Kombinace **Plzeň + Elektronika** záměrně neobsahuje žádné objednávky.

Tržby počítáme součtem sloupce `trzba`, počet objednávek počtem řádků
(nebo počtem unikátních ID) a průměr součtem tržeb děleným počtem objednávek.
Při nulovém počtu objednávek průměr neexistuje. Dashboard zobrazí pomlčku.

Soubor má kódování UTF-8 a čárku jako oddělovač. Příklady ho čtou pomocí
`pd.read_csv(cesta, parse_dates=["datum"])`. Data nejsou načítána z internetu.
Byla vygenerována deterministicky s náhodným seedem `20261021`.
