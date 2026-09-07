---
name: gdzie-stoje
description: >
  Podstawowy raport SEO „od zera" dla osoby nietechnicznej: wpisujesz domenę i dostajesz po ludzku —
  ile Google Cię pokazuje, które strony na to pracują, jak wypadasz na tle 3–5 konkurentów,
  gdzie są łatwe wygrane (frazy tuż pod topem), czy Twoje strony nie biją się ze sobą, oraz JEDNĄ rzecz
  do zrobienia w tym tygodniu. Dane z Senuto MCP (Baza 2.0); opcjonalnie OpenSEO (audyt techniczny, Search
  Console) — oba bez skryptów. Użyj, gdy user pyta „jak stoi moja strona w Google", „przeanalizuj moją
  domenę", „jak wypadam na tle konkurencji", „od czego zacząć SEO", „raport startowy", „gdzie stoję".
  NIE pisze treści (od tego /blisko-topu) i NIE analizuje jednego konkurenta w głąb (/luka-konkurencji).
---

# gdzie-stoje

**Dla kogo:** właściciel firmy, marketer bez SEO, klient na pierwszym spotkaniu. Nie zna słów „widoczność",
„striking distance", „kanibalizacja" — i nie musi. Raport ma **jedną stronę**, zaczyna się od werdyktu
i kończy jedną decyzją.

**Wymagania:** Senuto MCP. OpenSEO MCP opcjonalnie (dokłada audyt techniczny i dane z Google za 0 kredytów).
Zero skryptów, zero kluczy.

**Zużycie:** 5–8 zapytań z limitu `visibility_analysis_queries_per_day` Senuto (mimo nazwy limit jest
**miesięczny** — `hours_to_reset` ≈ 700 h; zwykle 400). Plus 1 zapytanie na każdego konkurenta dobranego ręcznie.
Zapytania z kroków 2–6 **nie zależą od siebie — wyślij je w jednej turze**, równolegle.

> Wersja 3.0 (2026-09-07): dochodzi **Krok 5b — filtr biznesowy z `extended` + wycena w złotych + kolumna AI Overview** (test: spogle.pl, krakowrolety.pl). Wcześniej: wersja 2.1 (2026-08-28) — po testach na krakowrolety.pl (lokalna usługa, 109 fraz), propdr.pl (sklep
> niszowy, 411 fraz), kulkowski.pl (mikro-domena, 15 fraz) i double-digital.pl (duża domena contentowa, 3 003 frazy). Wszystkie kształty pól poniżej są zweryfikowane
> na żywych odpowiedziach MCP, nie z dokumentacji.

---

## Zasada nadrzędna

**Liczby są tanie, osąd jest drogi.** Senuto zwróci 3 000 fraz; Twoja robota to powiedzieć, które
30 ma znaczenie i dlaczego. Każda liczba w raporcie ma być przetłumaczona na skutek dla firmy
(„ok. 1 300 osób miesięcznie szuka tego, a Ty jesteś na 21. miejscu — czyli praktycznie Cię nie widzą").

Trzy rzeczy, których nie wolno zrobić:
1. Nazywać `visibility` ruchem. To **szacunek** (pozycja × wyszukania × typowy CTR), nie dane z Google.
2. Chwalić za frazę, która nie przyniesie klienta (agencja na „papiery wartościowe" to nie sukces).
3. Wypisać 20 rekomendacji. Maksimum **7**, z czego jedna wyróżniona.

---

## Krok 0 — jedno zdanie o biznesie

Jeśli z kontekstu nie wiadomo, zapytaj **raz**: *„Czym zarabiacie i kto jest klientem?"* — to jedyny
filtr odróżniający „frazę z klientem" od „ruchu bez klienta".
**Tryb bez rozmowy** (automatyzacja, subagent, user nie odpowiada): pobierz stronę główną (`WebFetch`
lub `curl`, title + meta description zwykle wystarczą) i wpisz wniosek na górze raportu jako
**„Założenie o biznesie"** — oznaczone jako założenie, nie fakt.

Ustal od razu **typ domeny**, bo zmienia dwa dalsze kroki:
- **usługa lokalna** („rolety Kraków") → odsiew konkurentów po geografii, pasmo łatwych wygranych 4–25;
- **sklep** → klasyfikacja stron: główna / kategorie / karty produktów / blog;
- **firma/blog ogólnopolski** → domyślne ustawienia.

## Krok 1 — limity (darmowe)

`get_limits`. Jeśli `visibility_analysis_queries_per_day` ma mniej niż 8 zapytań do końca okresu —
powiedz to po ludzku i zrób wersję skróconą (kroki 2, 3b, 5 — bez konkurencji i kanibalizacji),
zaznaczając w raporcie, co pominięto.

## Krok 2 — stan: ile Google Cię pokazuje (1 zapytanie)

```
get_domain_statistics  domain, fetch_mode: "topLevelDomain", country_id: "200"
```
Czytaj z `summary.overview`: `top3`, `top10`, `top50`, `visibility`. AIO z `full_statistics.aio_keywords`
(frazy z ramką AI w wynikach) i `full_statistics.aio_visible_keywords` (w ilu z nich jesteś cytowany).

**Trendu z tego zapytania nie ma.** `full_statistics.*.diff` jest zawsze 0 (także z `days_compare_mode`),
a `get_positions_history_chart` dla Bazy 2.0 zwraca `no_data` — nie wywołuj go. Nośniki zmiany są dwa:
`position_diff` per fraza w kroku 3b (**ujemny = poprawa**, dodatni = spadek) oraz — lepszy —
`statistics.visibility.diff/percent` **per URL** z `get_urls extended` (krok 3a): tam różnice są realne
(u DD: wpis Meta Ads +63%, strona główna +91%). Trend w raporcie = suma zmian widoczności top 10–20 stron.
Jeśli wszystko 0 — pisz „brak danych o trendzie", nie „stabilnie".

Tłumaczenie dla laika (jedno zdanie, wszystkie trzy liczby):
> „Google pokazuje Twoją stronę przy **[top50]** zapytaniach, z czego na pierwszej stronie wyników
> jest **[top10]**, a w pierwszej trójce — **[top3]**."

**Zawsze `country_id: "200"`** (Baza 2.0). Baza 1.0 pokazuje ok. połowę fraz.

## Krok 3 — skąd ta widoczność (1–2 zapytania)

**3b. Frazy (zawsze):** `get_positions_data` `limit: 30`, `detail_level: "standard"`,
`order: {prop: "statistics.visibility.current", dir: "desc"}`.
Pola: `keyword, position, position_diff, visibility, searches, cpc, difficulty, url`. Zapamiętaj
`summary.total_keywords` — decyduje o kroku 5.

Przejrzyj top 30 i **wyłap artefakty** — trzy rodzaje, każdy pokazuj z udziałem w widoczności, licząc stan „bez niego":
- **fraza obok biznesu** z ogromnym wolumenem (u DD „linkd", 673 tys. wyszukań, poz. 7 → ~95% „widoczności");
- **wpisy obcojęzyczne** na polskiej domenie (u kulkowski.pl jeden wpis EN = 99,8% widoczności — ruch bez polskiego klienta);
- **fraza na temat, ale z mieszaną intencją** (samo „pdr" = 31% widoczności propdr; część szuka usługi, nie narzędzi) — tej nie wyrzucaj, pokaż udział.

**Marka** — trzy przypadki, nie jeden:
- nazwa firmy w danych i **poza top 3** → alarm numer jeden, przed wszystkim innym;
- nazwy **nie ma w danych** (mała domena, poniżej progu bazy) → „nie da się ocenić z tego raportu, sprawdź ręcznie w Google" — nie wnioskuj, że jest źle;
- nazwa jest **frazą generyczną** („Kraków Rolety", „Warszawa Okna") → test pomiń i napisz dlaczego.

**3a. Strony (gdy `total_keywords` > 30):** `get_urls` `limit: 20`, **`detail_level: "extended"` — obowiązkowo**.
`standard` zwraca tylko `keywords_count` (= liczba fraz w **top 10**, nie top 50 — stąd „0" przy stronach
z frazami dalej) i martwe `visibility_percent`. W `extended` czytaj
`all_urls[].statistics.{visibility,top3,top10,top50}.current`. `limit` potrafi zwrócić więcej wierszy, niż prosisz (20 → 24).
Adres z „›" (np. `double-digital.pl › blog/`) oznacza, że Google pokazuje na te frazy **stronę-listing** (kategorię,
blog, słownik) zamiast artykułu — to gotowa łatwa wygrana przez linkowanie wewnętrzne, zaznacz ją.
Przy domenie ≤ 30 fraz pomiń to zapytanie — udział stron policz z 3b (suma `visibility` per `url`).

Policz udział pierwszej strony w sumie widoczności z listy.
- **> 50% na jednym adresie** → napisz wprost: *„Połowa Twojej widoczności to jedna strona — jeśli spadnie,
  spada wszystko."* (krakowrolety: strona główna 70%; propdr: główna 45% + jedna karta produktu = 63%).
- Zaklasyfikuj adresy po ścieżce. Usługi: **usługi / blog / słownik / inne**. Sklep: **główna / kategorie /
  karty produktów / blog**. Podaj proporcję i wniosek po ludzku — typowe: „widoczność robi blog, a strony
  usługowe, na których zarabiasz, prawie nie istnieją" albo „widoczność robi strona główna i jeden produkt,
  kategorie, które sprzedają, są słabe".

## Krok 4 — na tle konkurencji (1–4 zapytania)

```
get_competitors  domain, fetch_mode: "topLevelDomain", country_id: "200", detail_level: "standard", limit: 15
```
Pola: `domain, common_keywords, is_main_domain, top3, top10, top50, visibility`. **Pierwszy wiersz to własna
domena** (`is_main_domain: true`) — `limit: 15` = 14 konkurentów.

Trzy scenariusze:
- **Lista ogólnopolska** (Wikipedia, Allegro, portale) → odsiej osądem, zostaw 3–5 domen, które **sprzedają to
  samo tej samej grupie**.
- **Nisza lokalna** — lista bywa czysto branżowa; wtedy odsiew jest **geograficzny**: zostaw firmy z tego samego
  miasta, odrzuć ogólnopolskie sklepy/producentów (wysoka `visibility`, niski `common_keywords`). Lokalność
  sprawdzaj `WebFetch` strony głównej — 0 zapytań Senuto.
- **Pusta lista lub < 3 sensowne domeny** (zdarza się w małych niszach — propdr: 0 wierszy; kulkowski: 1).
  **Nie ponawiaj** z `extended` ani Bazą 1.0 — też puste. Weź 2–3 domeny z wyników Google dla 1–2 głównych
  fraz (WebSearch, 0 zapytań) i dociągnij `get_domain_statistics` (1 zapytanie/domena, max 3). W tabeli
  usuń kolumnę „Wspólnych fraz" i napisz, że dobór jest ręczny. Gdy user nikogo nie wskazał i domena ma
  < 30 fraz — nie zgaduj: pokaż to, co jest, i jedno zdanie, że porównanie będzie możliwe, gdy domena urośnie.

Jeśli user wskazał konkurenta spoza listy — `get_domain_statistics` (max 2).

Werdykt w jednym zdaniu: *„Wyprzedzasz X i Y, ale Z ma 4× więcej fraz na pierwszej stronie."*
Nie rób analizy konkurenta w głąb — od tego jest `/luka-konkurencji`. Tu chodzi o **skalę i kierunek**.

## Krok 5 — łatwe wygrane (0–1 zapytanie)

**Jeśli `total_keywords` ≤ 60 — nie wysyłaj drugiego zapytania**, masz już wszystko w 3b (dla małej domeny
zwróciłoby ten sam zbiór). W przeciwnym razie:
```
get_positions_data  limit: 60, detail_level: "standard",
                    order: {prop: "statistics.searches.current", dir: "desc"}
```
Połącz z 3b, usuń duplikaty.

**Duża domena contentowa (> 500 fraz, blog/słownik):** sortowanie po wolumenie zwraca same generyki i definicje
(„podaż co to", „google ether"), a frazy z klientem giną w ogonie. Dołóż **trzeci przekrój — po CPC**:
```
get_positions_data  limit: 60, detail_level: "standard",
                    order: {prop: "statistics.cpc.current", dir: "desc"}
```
Wysoki CPC = ktoś płaci za ten klik = fraza sprzedażowa. U DD dopiero ten przekrój pokazał klaster „ile kosztuje
reklama w Google Ads" (5 fraz, poz. 9–15) i stronę usługi YouTube Ads na 15. — sortowanie po wolumenie nie wyciągnęło
żadnej z nich. CPC nadal nie pokazuj w raporcie; użyj go tylko do selekcji („reklamodawcy płacą za tę frazę 50–300 zł").

**Pasmo pozycji:** domyślnie **4–15**. **Usługa lokalna: 4–25** — najcenniejsze frazy „[usługa] [miasto]"
zwykle wiszą na 2.–3. stronie (krakowrolety: „rolety kraków" 1 300/mies. na 21., „plisy kraków" 480 na 22.).
**Niezależnie od pasma** wypisz osobno 3 frazy z największym wolumenem na pozycjach 16–30 — „duże, ale dalej".
To bardzo często jest właściwa „jedna rzecz w tym tygodniu", a sztywne pasmo by ją wycięło.

**Odsiew — bez tego lista jest w 80% śmieciem:**

| Wyrzuć | Jak poznać |
|---|---|
| literówki / pomyłki | fraza brzmi jak inny temat („google ether" na stronie o E-E-A-T) |
| jednowyrazowe generyki | „marketing", „seo", „ctr" — rozjechana intencja |
| cudze marki | „mailchimp", „orlita", „krakżal" — nie przejmiesz |
| ruch bez klienta | pasuje do treści, nie do biznesu („bateria makita" w sklepie PDR) |
| za mały wolumen | < 20 wyszukań/mies. — chyba że reszta listy jest jeszcze mniejsza |
| `position: 51` z pustym `url` | to „poza top 50", nie 51. miejsce |
| `url` bez ukośnika / z „›" | breadcrumb, nie adres — oznacz „do sprawdzenia" |

**Zostaw** tylko frazy, przy których dokończysz zdanie: *„człowiek, który to wpisuje, może u nas kupić,
bo…"*. Wybierz **5–8**. Dla każdej: fraza · pozycja · ile osób pyta/mies. · która strona · jedno zdanie
„dlaczego warto". Jeśli Google pokazuje na frazę **nie tę stronę, co powinien** (kategorię bloga zamiast
oferty) — to jest właśnie łatwa wygrana, napisz to.

**Mała domena:** jeśli po odsiewie zostało < 3 fraz — rozszerz pasmo do 4–35 i **napisz to w tabeli**
(„daleko, ale w zasięgu"). Jeśli nadal 0 — sekcja zmienia nazwę na **„Od czego zacząć"** i wskazuje 2–3 tematy
z klientem, na które trzeba dopiero zbudować stronę.

Nie pisz tu tytułów ani treści — zakończ: *„Dla trzech pierwszych `/blisko-topu` przygotuje gotowy
tekst do wklejenia."*

## Krok 5b — filtr biznesowy i wycena (v3, 1 zapytanie)

Krok 5 odsiewa osądem. Ten krok dokłada **twarde dane o intencji**, których `standard` nie ma:
```
get_positions_data  limit: 50, detail_level: "extended",
                    order: {prop: "statistics.cpc.current", dir: "desc"}     # frazy, za które ktoś płaci
```
Odpowiedź ma ~100 kB → zapisz do pliku i przepuść przez parser (albo czytaj ręcznie):
```
python3 ~/.claude/skills/_senuto-wspolne/senuto_extended.py positions_extended.json --bofu --min-searches 30
```
Kolumny: `poz · hist (pierwszy→ostatni pomiar) · w/l · stage (tofu/mofu/bofu) · szuk · cpc · AIO · PAA · url`.

**Trzy reguły czytania:**
1. **`journey_stage` bywa błędny przy frazach lokalnych i wynajmowych** — „dmuchańce warszawa" (CPC 8,64 zł) ma `tofu`.
   Gdy stage mówi `tofu`, a CPC ≥ 5 zł → traktuj jak frazę z klientem. Gdy stage `bofu`, a CPC 0 i fraza brzmi
   jak nazwa firmy („krakżal rolety") → cudza marka, wyrzuć.
2. **Kolumna AIO** = przy tej frazie Google pokazuje odpowiedź AI. Zestaw z `aio_visible_keywords` z kroku 2.
   Strona cytowana w AIO = **zakaz przebudowy** (reguła z `/blisko-topu`). Dla usług lokalnych AIO jest rzadkie
   (krakowrolety: 2 frazy z 106), dla contentu częste (spogle: 909 z 1 884; cytowany w 230).
3. **Kolumna `map`** (`get_characteristics_table characteristics: "serp_params"`, 1 zapytanie, cała domena) —
   jeśli `map` robi > 30% widoczności (krakowrolety: 39%), pierwsza rekomendacja raportu to wizytówka Google,
   nie treść. Napisz to w „Jednej rzeczy", jeśli user nie ma GBP.

**Wycena** — zamiast pozycji pokaż złotówki, bo laik rozumie złotówki:
```
zysk_klików/mies. = szukania × (CTR(3) − CTR(pozycja_teraz))       CTR: 1→27%, 2→15,6%, 3→10,4%, 4→7,5%, 5→5,4%,
wartość_zł/mies.  = zysk_klików × min(CPC, 60)                          6→4%, 8→2,6%, 10→1,9%, 11–15→1,2%, 16–20→0,8%, 21–30→0,4%
```
Przykład: „rolety kraków" 1 300 × (10,4% − 0,4%) × 20,74 zł ≈ **2 700 zł/mies.** na 25. miejscu. Podaj jako rząd wielkości.

**Agregacja po stronie:** zsumuj wartość fraz per `url`. Wynik: „3 strony niosą 80% Twojego potencjału" — to jest
lista do roboty, nie 40 fraz. U krakowrolety strona główna niesie „rolety kraków", „plisy kraków", „żaluzje kraków",
„rolety zewnętrzne kraków" (łącznie ~2 600 szukań/mies., poz. 22–38) — czyli jedna strona próbuje wygrać cztery
tematy i nie wygrywa żadnego → rekomendacja to **wydzielenie podstron**, nie „popraw stronę główną".

Sekcja raportu „Łatwe wygrane" dostaje dwie kolumny więcej: **„Warte ok. zł/mies."** i **„AI"** (✓ = jest AIO,
★ = jesteś cytowany). Wysokość CPC nadal nie pokazuj — tylko wynik mnożenia.

## Krok 6 — czy Twoje strony nie biją się ze sobą (1 zapytanie)

```
get_cannibalization_keywords  domain, fetch_mode: "topLevelDomain", country_id: "200", detail_level: "standard"
```
Pola: `keyword, position, position_diff, current_url, previous_url, searches, visibility` + `summary.severity`
(NONE / LOW / MEDIUM / HIGH). **Senuto pokazuje, że adres rankujący na frazę ZMIENIŁ SIĘ między pomiarami** —
nie ma pozycji drugiej strony, więc „obie w top 20" jest niesprawdzalne. Wybieraj po `searches`.

Najpierw **oddziel duplikaty techniczne** — ten sam slug pod dwoma adresami (`httpswwwpropdrpl…`,
`/lampy-male` vs `/male-lampy`, http/https, z i bez ukośnika) — oraz **stare adresy po zmianie linków**: gdy
`previous_url` wygląda jak dłuższa/starsza wersja `current_url`, sprawdź `curl -o /dev/null -w "%{http_code}"`
(0 zapytań). **301 → to nie kanibalizacja, tylko opóźnienie Senuto** — idzie do „Co już działa" („przekierowania
działają"). U DD z 71 zgłoszonych ~2/3 to były już przekierowane stare slugi; prawdziwych walk zostało 5. To nie jest walka treści, tylko przekierowanie
do zrobienia → idzie do „Przeszkody technicznych" albo do „Jednej rzeczy", nie do tabeli walk.

Z reszty weź **maksymalnie 3** o największym `searches`. Po ludzku: *„Na frazę „X" Google waha się między
Twoimi stronami A (teraz) i B (wcześniej) — przez to żadna nie jest wysoko. Jedna ma być główna, druga
linkuje do niej albo znika."*
`severity: NONE` albo LOW z frazami < 50 wyszukań → jedno zdanie w „Co już działa", bez tabeli.

## Krok 7 — opcjonalnie, jeśli jest OpenSEO (0 kredytów)

- **Audyt techniczny:** `run_site_audit` (`maxPages: 150`, `runLighthouse: false`) → `get_audit_issues`
  `severity: "critical"`. Do raportu trafiają **tylko** rzeczy, które laik zrozumie i które realnie
  szkodzą: strony 404 linkowane z innych stron, `noindex` na stronach usługowych, łańcuchy przekierowań,
  duplikaty adresów z kroku 6. Max 3. Bez `auditId` narzędzie bierze **ostatni** audyt projektu — jeśli był
  mniejszy/inny, podaj `auditId` tego właściwego (u DD ostatni audyt zwrócił 0 krytycznych, a 150-stronicowy z dnia
  wcześniej miał 12 zepsutych linków). Znalezisko zawsze potwierdź `curl`-em przed wpisaniem do raportu.
- **Sprawdzian z rzeczywistością:** jeśli GSC jest podpięte do projektu OpenSEO —
  `get_search_console_performance` `dateRange: last_28_days`, `dimensions: ["page"]`, `rowLimit: 10`.
  Zestaw kliknięcia z Google z szacunkiem Senuto. Rozjazd > 3× → napisz, że szacunek jest tylko szacunkiem.
  GSC podpina się **per projekt** — sprawdź narzędziem, nie zakładaj.

Bez OpenSEO pomiń krok bez komentarza (nie pisz „zainstaluj OpenSEO" w raporcie klienta).

## Krok 8 — raport

Zapisz do `audyt/gdzie-stoje-[domena]-[YYYY-MM-DD].md` — w katalogu projektu klienta, jeśli w nim pracujesz;
inaczej w bieżącym katalogu. Powiedz userowi, gdzie zapisałeś.

Struktura — **w tej kolejności**:

```markdown
# Gdzie stoi [domena] w Google — [data]

> **Założenie o biznesie:** [tylko gdy wnioskowane ze strony, nie z rozmowy]

## Werdykt
[2–3 zdania: skala, największa szansa, największe ryzyko. Bez żargonu.]

## Jeśli zrobisz tylko jedną rzecz w tym tygodniu
**Co:** … **Dlaczego:** [liczba z danych]
1. … 2. … 3. …
**Jak sprawdzisz, że zadziałało:** [np. za 4 tygodnie fraza „…" w top 3 / ponów ten raport]

## Ile Google Cię pokazuje
| | Twoja strona | [konkurent 1] | [konkurent 2] | … |
|---|---|---|---|---|
| Fraz w top 50 | | | | |
| Fraz na 1. stronie | | | | |
| Fraz w top 3 | | | | |
[kolumny konkurentów: tyle, ilu jest; przy doborze ręcznym — zaznacz]
[1 zdanie: trend z position_diff albo „brak danych o trendzie"; 1 zdanie o artefakcie, jeśli był;
 1 zdanie o ramce AI: „Google pokazuje odpowiedź AI przy X Twoich frazach, w Y z nich cytuje Ciebie"]

## Co na to pracuje
[proporcja usługi/blog… lub główna/kategorie/produkty…; koncentracja na jednym adresie, jeśli > 50%; marka]

## Łatwe wygrane (5–8)            ← dla mikro-domeny: „Od czego zacząć"
| Fraza | Pozycja | Pyta/mies. | Strona | Dlaczego warto |
[+ „Duże, ale dalej": 3 frazy z pozycji 16–30]
[+ 2–3 odrzucone z powodem — to często najbardziej otwierająca oczy część]

## Strony, które biją się ze sobą (max 3)      ← przy NONE/LOW: jedno zdanie w „Co już działa"
| Fraza | Pyta/mies. | Strona teraz | Strona wcześniej | Co zrobić |

## Co już działa
[3–5 rzeczy: frazy z klientem w top 3, marka na 1., brak kanibalizacji, cytowania w ramce AI…]

## [opcjonalnie] Przeszkody techniczne (max 3)
[duplikaty adresów z kroku 6, wyniki audytu OpenSEO]

## Czego ten raport nie widzi
- widoczność to szacunek, nie ruch z Google (chyba że podpięto Search Console);
- dane z jednego pomiaru Senuto (data: …); trend: [z position_diff / brak];
- nie sprawdzaliśmy lokalnych wyników w Mapach ani linków — to osobne analizy;
  [usługa lokalna: „dla firmy usługowej z miasta Mapy Google są zwykle głównym źródłem klientów — ten raport
  ich nie obejmuje" — to nie przypis, tylko główne ograniczenie];
- [jeśli dobór ręczny: „konkurenci dobrani ręcznie z wyników Google, bez danych o wspólnych frazach"].
```

**Reguły formy:**
- Termin techniczny przy pierwszym użyciu — jedno zdanie po ludzku. Bez „SERP", „CTR", „striking distance",
  „kanibalizacja" w nagłówkach.
- Liczby zaokrąglone („ok. 1 900 osób"), CPC nie pokazuj (bywa absurdalne).
- Żadnych obietnic „wzrost o X%". Tylko: co, dlaczego, jak sprawdzić.

## Pułapki Senuto zaszyte w tym skillu

- `country_id: "200"` do pomiaru; `get_keywords` / `get_questions` / `get_groups` tylko Baza 1.0 — tu ich nie używamy.
- `get_urls`: `standard` **nie ma** `statistics` — używaj `extended`; `keywords_count` = frazy w top 10; `visibility_percent` = 0 zawsze; `limit` zwraca więcej niż prosisz; `statistics.visibility.diff` per URL = jedyny działający trend.
- `get_positions_data` nie filtruje po treści frazy — przekrój po **CPC** jest jedynym sposobem wyłowienia fraz sprzedażowych z dużej domeny.
- Kanibalizacja zawiera stare slugi po redirectach — weryfikuj `curl`-em, 301 wyklucz.
- `get_domain_statistics`: wszystkie `diff` = 0, `days_compare_mode` nic nie zmienia; wykres historii → `no_data`. Trend tylko z `position_diff` (ujemny = poprawa).
- `get_competitors`: pierwszy wiersz = własna domena; bywa **pusty** dla nisz — wtedy dobór ręczny, nie ponawianie.
- `get_cannibalization_keywords`: `current_url` / `previous_url` (zmiana adresu w czasie), nie dwa adresy naraz; ma `summary.severity`.
- `position: 51` + `url: ""` = poza top 50.
- `detail_level: "standard"` nie ma `intentions` ani `snippets`; `extended` (krok 5b) ma je + `position.history` + `trends.history`, ale waży ~100 kB na 50 fraz — parsuj skryptem.
- `journey_stage` z Senuto myli się na frazach lokalnych/wynajmowych — CPC ≥ 5 zł bije etykietę `tofu`.
- Moduł SERP (`serp_create`) → 402 Paywall mimo limitu 6000/dzień — limit ≠ dostęp.
- `get_limits` darmowe; wszystko inne zjada limit — nie dociągaj stron „na zapas".
