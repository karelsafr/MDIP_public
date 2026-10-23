# Data pro cukrárnu

Tři CSV soubory popisují **14 surovin, 6 receptů a 39 položek receptů**. Data i ceny jsou smyšlené a slouží k výuce. Nejde o ceník skutečné cukrárny ani o aktuální ceny v obchodech. Postupy jsou zkrácené výukové texty, nikoli ověřené cukrářské receptury.

Soubory používají UTF-8, čárku jako oddělovač sloupců a tečku jako desetinný oddělovač. Textové identifikátory `R01` a `S01` ponechte jako text. Názvy výrobků a surovin jsou popisky; tabulky propojujte pomocí identifikátorů.

## 1. Ceník surovin

Soubor [suroviny.csv](suroviny.csv). Jeden řádek představuje jednu surovinu a její výukové balení.

| Sloupec | Význam | Příklad |
|---|---|---|
| `surovina_id` | Jedinečný identifikátor suroviny. | `S03` |
| `nazev_suroviny` | Název pro tabulku a graf. | Máslo |
| `jednotka` | Jednotka množství: `g`, `ml` nebo `ks`. | `g` |
| `velikost_baleni` | Množství v jednom balení v uvedené jednotce. | 250 |
| `cena_baleni_kc` | Cena celého balení v Kč. | 60 |

Například 200 g másla stojí v modelu `200 / 250 × 60 = 48 Kč`. Počítáme **náklad spotřebované suroviny**, nikoli hotovost potřebnou k nákupu celých balení. Zbytek balení zůstává dostupný pro další výrobu.

## 2. Recepty a prodejní ceny

Soubor [recepty.csv](recepty.csv). Jeden řádek představuje **jednu výrobní dávku** jednoho výrobku.

| Sloupec | Význam |
|---|---|
| `recept_id` | Jedinečný identifikátor receptu, například `R01`. |
| `nazev` | Název výrobku. |
| `kategorie` | Skupina pro filtr: Řezy, Dorty, Odpalované, Drobné pečivo nebo Tartaletky. |
| `kusu_davka` | Počet prodejných kusů z jedné dávky. U dortu jde o počet porcí. |
| `prodejni_cena_kc` | Prodejní cena **jednoho kusu**, nikoli celé dávky. |
| `prace_min_davka` | Modelová doba práce na jednu dávku v minutách. Nejde o celkový čas pečení a chladnutí. |
| `ostatni_naklady_davka_kc` | Ostatní náklady jedné dávky, například modelový podíl energie a obalů. |
| `postup` | Zkrácený pracovní postup. Jednotlivé kroky odděluje znak `\|`. |

V makronkovém receptu `R05` znamená 20 kusů **20 hotových slepených makronek**, tedy 40 skořápek. Položka vejce účtuje nákup čtyř celých vajec; model nepřipisuje žádnou úsporu za další využití žloutků.

## 3. Složení receptů

Soubor [polozky_receptu.csv](polozky_receptu.csv). Jeden řádek představuje jednu surovinu v **jedné dávce receptu**.

| Sloupec | Význam |
|---|---|
| `recept_id` | Odkaz na recept v `recepty.csv`. |
| `surovina_id` | Odkaz na surovinu v `suroviny.csv`. |
| `mnozstvi` | Spotřeba na jednu dávku, ve stejné jednotce, jakou má surovina v ceníku. |

Pár `recept_id` + `surovina_id` se neopakuje. Každý odkaz vede na existující recept nebo surovinu. Všechny ceny, velikosti balení, množství a výtěžnosti jsou kladné. Propojování podle `surovina_id` nemá měnit počet 39 položek.

## Pravidla kalkulace

Pro obě závěrečné úlohy použijte **sazbu práce 240 Kč za hodinu**, tedy 4 Kč za minutu. Cena surovin a sazba práce jsou pro všechny výpočty stejné.

1. **Náklad jedné položky:** množství / velikost balení × cena balení.
2. **Suroviny na dávku:** součet nákladů všech položek daného receptu.
3. **Práce na dávku:** minuty práce / 60 × 240 Kč.
4. **Celkový náklad na dávku:** suroviny + práce + ostatní náklady na dávku.
5. **Náklad na kus:** náklad na dávku / počet kusů z dávky.
6. **Modelový zisk na kus:** prodejní cena kusu − náklad na kus.
7. **Modelová marže v %:** modelový zisk na kus / prodejní cena kusu × 100.

Marže má ve jmenovateli **prodejní cenu**. Dělení nákladem by počítalo jiný ukazatel, přirážku. Záporný modelový zisk i zápornou marži zobrazte; nepřevádějte je na nulu.

Model nezahrnuje fixní režii provozovny, DPH ani daně. Výraz **modelový zisk** proto označuje pouze výsledek této kalkulace, nikoli skutečný čistý zisk cukrárny. Soubor neobsahuje skutečné prodeje. Zisky na jeden kus různých výrobků nesčítejte a neoznačujte takový součet za zisk provozovny.

Počet dávek `d` může být 1, 2 nebo 3. Množství surovin, počet kusů, minuty práce a všechny náklady násobíme `d`; model nepředpokládá množstevní slevy ani úspory při společném pečení. Náklad a zisk na jeden kus se nemění. Zisk z celé výroby je jen **modelový zisk při prodeji všech vyrobených kusů** za zadanou cenu.

Nezaokrouhlujte mezivýpočty. Zaokrouhlení použijte až při zobrazení peněžních hodnot a procent.

## Kontrolní hodnoty

| Kontrola | Očekávaná hodnota |
|---|---:|
| Výrobky v celé nabídce | 6 |
| Kategorie v nabídce | 5 |
| Recepty v kategorii Řezy | 2 |
| Výrobky se záporným modelovým ziskem | 1: Čokoládová makronka |
| Brownie: suroviny na dávku | 162,76 Kč |
| Brownie: práce na dávku | 140 Kč |
| Brownie: celkový náklad na dávku | 338,76 Kč |
| Brownie: náklad na kus | 28,23 Kč |
| Brownie: modelový zisk na kus | 30,77 Kč |
| Brownie: dvě dávky | 24 kusů; náklad 677,52 Kč |
| Brownie: modelový zisk ze dvou dávek při prodeji všeho | 738,48 Kč |
| Makronka: náklad na dávku | 644,18 Kč |
| Makronka: náklad na kus, před zaokrouhlením | 32,209 Kč |
| Makronka: modelový zisk na kus, před zaokrouhlením | −10,209 Kč |

Zadání a náhledy cílových výstupů jsou v [závěrečných úlohách](../../ZAVERECNE_ULOHY/README.md).
