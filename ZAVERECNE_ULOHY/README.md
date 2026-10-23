# Závěrečné úlohy: cukrárna

Vytvořte dva nové výstupy nad stejnými daty: **PDF přehled nabídky cukrárny** a **aplikaci s přehledem výrobků a receptářem**. Na snímcích a níže jsou vzorové výsledky, podle kterých poznáte, co má vaše řešení umět. Přesné barvy ani rozmístění nemusíte kopírovat.

Data jsou v [data/cukrarna](../data/cukrarna/POPIS_DAT.md). Obsahují 14 surovin s cenou balení, 6 receptů na celé dávky a 39 položek receptů. Všechny ceny a receptury jsou smyšlené výukové údaje. Popis dat vysvětluje jednotky, propojení tabulek i model výpočtu.


Vytvořte vlastní soubory `Plotly/Plotly11_Cukrarna.py` a `Dash/Dash13_Cukrarna.py`. Číslované příklady z workshopu používejte jako reference. Každý nový skript má fungovat samostatně. Vyřešené skripty těchto dvou úloh nejsou součástí studentského balíčku.

## Společný datový základ

Načtěte všechny tři CSV. Položky receptů propojte s ceníkem přes `surovina_id`. Každé položce dopočítejte náklad spotřebované suroviny, položky sečtěte podle `recept_id` a souhrn připojte k tabulce receptů.

Použijte sazbu práce **240 Kč/hodinu**:

| Výsledek | Výpočet |
|---|---|
| Náklad položky receptu | množství / velikost balení × cena balení |
| Suroviny na dávku | součet nákladů položek receptu |
| Práce na dávku | minuty práce / 60 × 240 |
| Náklad na dávku | suroviny + práce + ostatní náklady na dávku |
| Náklad na kus | náklad na dávku / počet kusů z dávky |
| Modelový zisk na kus | prodejní cena − náklad na kus |
| Modelová marže v % | modelový zisk / prodejní cena × 100 |

Množství a velikost balení musejí mít stejnou jednotku. Cena v `recepty.csv` je za **jeden kus**; spotřeba surovin, práce a ostatní náklady jsou za **celou dávku**. Zaokrouhlujte až zobrazené výsledky.

Model zahrnuje suroviny, práci a uvedené ostatní náklady. Nezahrnuje fixní režii, DPH ani daně. V reportu a aplikaci používejte označení **modelový zisk** a tento rozsah krátce vysvětlete. Data neobsahují skutečné prodeje.

## Úloha 1: jednostránkový PDF report

**Výchozí reference:** [Plotly07](../Plotly/Plotly07.py), [Plotly08](../Plotly/Plotly08.py), [Plotly09](../Plotly/Plotly09.py) a [Plotly10](../Plotly/Plotly10.py).

### Co má vzniknout

PDF pro člověka, který se chce rychle zorientovat v nabídce a v nákladech na jednotlivé výrobky. Celou stránku sestavte v Plotly a exportujte pomocí Kaleida. Nepotřebujete Word, ReportLab ani skládání několika PDF.

Report má obsahovat:

- Nadpis a viditelné označení syntetických dat.
- Tři ukazatele: počet výrobků, nejvyšší modelový zisk na kus a počet ztrátových výrobků.
- Všech šest výrobků s čitelnými názvy a jednotkami Kč/kus.
- Porovnání prodejní ceny a celkového nákladu na jeden kus.
- Rozpad nákladu na kus na suroviny, práci a ostatní náklady.
- Přehled modelového zisku na kus a modelové marže; můžete použít graf nebo tabulku.
- Výrazné rozlišení výrobku se záporným modelovým ziskem.
- Krátký komentář vypočtený z dat, například který výrobek má nejvyšší modelový zisk na kus a který je ztrátový.
- Vysvětlení modelu a zdroje dat. Jednotky a hlavní sdělení musí být čitelné i bez hoveru.

Výstup uložte jako `vystupy/cukrarna_report.pdf`. Pro kontrolu můžete uložit také PNG nebo HTML. Součet zisků na kus různých výrobků není celkový zisk provozovny a nemá být prezentován jako takový ukazatel.

### Vzorový výsledek

[Otevřít cílový PDF report](cukrarna_report_vzor.pdf) · [Náhled reportu](cukrarna_report_vzor.png)

### Doporučený postup

1. Nejprve vypište kalkulaci šesti výrobků do konzole a ověřte kontrolní hodnoty níže.
2. Vytvořte jednotlivé grafy a teprve potom je vložte do společné figury.
3. Přidejte ukazatele a komentář pomocí anotací. Pro delší text použijte zalomení a odpovídající okraje.
4. Exportujte PDF a otevřete jej. Ověřte celou stránku, nejen úspěšné dokončení Pythonu.

### Kontrola dokončeného řešení

- Report má jednu stránku a obsahuje všech šest výrobků.
- U brownie vychází náklad **28,23 Kč/kus** a modelový zisk **30,77 Kč/kus**.
- Čokoládová makronka má záporný modelový zisk; její náklad je vyšší než cena.
- Součet tří nákladových složek odpovídá celkovému nákladu výrobku.
- Při změně vstupní ceny suroviny se po novém spuštění změní příslušná čísla, grafy i komentář.

## Úloha 2: dashboard se dvěma záložkami

**Výchozí reference:** [Dash09](../Dash/Dash09.py), [Dash10](../Dash/Dash10.py) a [Dash12](../Dash/Dash12.py). Novým prvkem jsou `dcc.Tabs` a `dcc.Tab`; jejich základní použití je vysvětlené v prezentaci a v [oficiální dokumentaci](https://dash.plotly.com/dash-core-components/tabs).

### Záložka „Nabídka a zisk“

Uživatel má porovnat výrobky a případně omezit nabídku na jednu kategorii.

- Filtr kategorie s výchozí volbou **Všechny**.
- Tři karty: **počet výrobků ve výběru**, **nejvyšší modelový zisk na kus** a **počet ztrátových výrobků ve výběru**.
- Graf porovnávající prodejní cenu s nákladem na kus.
- Graf modelového zisku na kus se zřetelnou nulou a viditelnými zápornými hodnotami.
- Karty i oba grafy používají stejný výběr. Návrat na Všechny obnoví celou nabídku.

[Náhled záložky Nabídka a zisk](cukrarna_nabidka_vzor.png)

### Záložka „Receptář“

Uživatel má vybrat výrobek, prohlédnout recept a přepočítat jej na více dávek.

- Výběr receptu podle názvu, s identifikátorem receptu jako jeho hodnotou. Výchozí recept je **Čokoládové brownie**.
- Výběr **1, 2 nebo 3 dávek**.
- Tři karty: **počet vyrobených kusů**, **celkový náklad zvolených dávek** a **modelový zisk při prodeji všech těchto kusů**.
- Tabulka surovin s názvem, přepočteným množstvím, jednotkou a nákladem spotřebované suroviny.
- Pracovní postup přehledně po jednotlivých krocích. Text v CSV je oddělený znakem `|`.
- Graf nákladů jednotlivých surovin pro zvolený recept a počet dávek.
- Jasné označení, co se zobrazuje na kus a co za celou zvolenou výrobu.

[Náhled záložky Receptář](cukrarna_receptar_vzor.png)

Počet dávek násobí množství surovin, počet kusů, práci i ostatní náklady. Náklad a modelový zisk na kus zůstávají stejné. Zisk celé výroby je předpoklad **prodeje všech vyrobených kusů**, nikoli údaj o uskutečněném prodeji.

### Doporučený postup

1. Použijte ověřenou kalkulaci z PDF úlohy. Pokud začínáte touto úlohou, ověřte nejprve společné výpočty v konzoli.
2. Připravte obě záložky jako obsah komponent `dcc.Tab`. Pro tuto malou aplikaci není potřeba obsah záložek vytvářet dalším callbackem.
3. Propojte filtr kategorie s kartami a grafy první záložky.
4. Propojte výběr receptu a počtu dávek s obsahem receptáře. Všechny související výstupy přepočítejte ze stejných vstupů.
5. Vyzkoušejte přepínání záložek, různé kategorie, všechny recepty a všechny tři počty dávek.

Po úpravě Python kódu použijte Stop, Run a obnovení stránky. Před spuštěním nového příkladu zastavte předchozí server na portu 8050.

### Kontrolní scénáře

| Akce | Očekávaný výsledek |
|---|---|
| Nabídka: Všechny | 6 výrobků; 1 ztrátový výrobek. |
| Nabídka: Řezy | 2 výrobky, brownie a citronový řez; žádný ztrátový. |
| Nabídka: Drobné pečivo | Pouze makronka; záporný zisk je vidět v kartě i grafu. |
| Návrat na Všechny | Znovu všech 6 výrobků. |
| Receptář: brownie, 1 dávka | 12 kusů; náklad 338,76 Kč; modelový zisk při prodeji všeho 369,24 Kč. |
| Receptář: brownie, 2 dávky | 24 kusů; náklad 677,52 Kč; modelový zisk při prodeji všeho 738,48 Kč. |
| Receptář: brownie, 2 dávky, máslo | 400 g; náklad másla 96 Kč. |
| Receptář: makronka, 1 dávka | 20 kusů; náklad 644,18 Kč; modelový zisk při prodeji všeho −204,18 Kč. |
| Změna receptu a návrat na brownie | Žádné staré suroviny ani hodnoty z předchozího receptu. |

Prázdný výběr může vzniknout po změně dat nebo během rozšiřování aplikace. V takovém případě zobrazte vysvětlení; nevydávejte neexistující maximum za nulu a nenechávejte na stránce staré výsledky.

## Co předvést na konci / co douručit

Ukažte PDF nebo obě záložky své aplikace. Na jednom konkrétním výrobku vysvětlete cestu od ceny balení suroviny přes náklad dávky až k modelovému zisku na kus. Potom předveďte změnu vstupu a doložte ji jedním kontrolním výpočtem.

Pro rozšíření můžete přidat vlastní výrobek, změnit sazbu práce nebo umožnit zadat novou prodejní cenu. Nejdříve dokončete a ověřte základní variantu.
