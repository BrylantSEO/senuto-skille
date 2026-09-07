---
name: dlaczego-daleko
description: >
  Odpowiada na pytanie „jestem na 12. (20., 25.) miejscu na frazę X — DLACZEGO?". Bierze domenę + jedną frazę,
  czyta z Senuto MCP pozycję, intencję i cechy SERP-u, pobiera żywy SERP (Chrome MCP), crawluje stronę usera
  i top10 (Crawl4AI z pruningiem) i przechodzi drabinę diagnozy od najtańszej do najdroższej przyczyny:
  zły typ strony → local pack / AI Overview / PAA → struktura (mierzona z realnego top10, nie z badania)
  → brakujące podtematy (analiza semantyczna TF-IDF). Kończy się JEDNYM zdaniem werdyktu i listą braków.
  Użyj, gdy user pyta „dlaczego jestem tak nisko", „czemu nie rankuję na X", „co ma konkurencja, czego ja nie mam
  na tej frazie", „co poprawić na stronie Y". NIE pisze treści (od tego /blisko-topu) i NIE analizuje całej
  domeny (od tego /gdzie-stoje, /luka-konkurencji).
---

# dlaczego-daleko

**Dla kogo:** właściciel, który dostał z `/gdzie-stoje` albo `/luka-konkurencji` frazę do poprawy i chce wiedzieć,
**co konkretnie** przegrywa — zanim zleci komukolwiek „dopisanie treści".

**Wymagania:** Senuto MCP + Chrome MCP (do SERP-u) + Python z `crawl4ai` (`pip install crawl4ai &&
python3 -m playwright install chromium` — jednorazowo). Skrypty w `~/.claude/skills/_senuto-wspolne/`:
`crawl_serp.py`, `topic_gap.py`. Bez `.env`, bez kluczy API.
**Zużycie:** 1–2 zapytania Senuto (`visibility`), 0 SERP-owych (moduł SERP Senuto jest na większości planów
paywallowany — sprawdzone: `serp_create` → 402 mimo limitu 6000/dzień).

> Wersja 1.0 (2026-09-07) — przetestowana na „rolety kraków" (krakowrolety.pl, poz. 25) i „wynajem dmuchańców"
> (spogle.pl, poz. 29). Odtwarza utracony `/blisko-topu-pro` z trzema zmianami: drabina diagnozy z przerwaniem,
> analiza semantyczna bez klucza API, Chrome MCP jako źródło domyślne.

---

## Zasada nadrzędna

**Nie zakładaj, że problemem jest długość.** W teście na „media plan" strona usera miała 12 unikalnych liczb przy
medianie top10 = 5 i przegrywała granulacją (4 nagłówki vs 7) i brakiem list (0 vs 10). „Dopisz treści" byłoby
złą radą. **Poprzeczkę mierzysz z realnego top10 tej frazy**, nie z badań na 150 stronach EN.

Druga zasada: **drabina z przerwaniem.** Sprawdzasz przyczyny od najtańszej. Jeśli na szczeblu 1 wychodzi,
że w top10 są wyłącznie oferty, a user rankuje blogiem — **nie crawlujesz**, bo żadna poprawka treści tego nie naprawi.
Werdykt na szczeblu 1 jest tak samo pełnoprawny jak na szczeblu 4.

---

## Krok 0 — fraza i biznes

Wejście: **domena + jedna fraza** (+ opcjonalnie URL strony, która ma rankować). Jeśli user podał tylko domenę —
odeślij do `/gdzie-stoje` (tam wychodzi, na co warto). Jedno zdanie o biznesie jak w innych skillach.

## Krok 1 — co mówi Senuto o tej frazie (1–2 zapytania)

`get_positions_data` nie filtruje po frazie, więc:
```
get_positions_data  domain, country_id: "200", detail_level: "extended", limit: 50,
                    order: {prop: "statistics.cpc.current", dir: "desc"}      # frazy kupujące
```
(albo `order` po `searches` dla fraz o dużym wolumenie). Odpowiedź jest duża (~100 kB) — zapisz do pliku i:
```
python3 ~/.claude/skills/_senuto-wspolne/senuto_extended.py positions_extended.json | grep -i "<fraza>"
```
Z wiersza odczytaj: **pozycja · historia (pierwszy→ostatni punkt) · `journey_stage` · CPC · AIO/PAA/map · URL**.
Jeśli frazy nie ma w 50 → user jest poza top50 albo fraza jest poza bazą; napisz to i jedź dalej z SERP-em.

Dwie rzeczy do zanotowania od razu:
- **`journey_stage` bywa błędny** — „dmuchańce warszawa" (CPC 8,64 zł, czysto wynajmowa) ma `tofu`. Gdy stage mówi
  tofu, a CPC ≥ 5 zł, wierz CPC.
- **`url.current`** — czy rankuje ta strona, która powinna? Strona główna / kategoria bloga zamiast oferty to
  osobna diagnoza (patrz szczebel 1).

## Krok 2 — żywy SERP (0 zapytań Senuto)

Drabina źródeł: **1. Chrome MCP** (domyślnie) → 2. moduł SERP Senuto (`serp_create`/`serp_get_report`, tylko jeśli plan
go ma) → 3. user wkleja 10 pierwszych linków.

Chrome: `https://www.google.com/search?q=<fraza>&hl=pl&gl=pl`, potem ekstraktor JS z
`~/.claude/skills/_senuto-wspolne/google-serp-chrome.md` (organic z dedup po hostname, PAA, AIO + źródła, local pack).
**Wynik JS ucina się przy ~1 500 znakach** — wyciągaj organic i PAA/AIO w dwóch wywołaniach albo skracaj tytuły.
Zapisz jako `data/dlaczego-daleko/<slug>/serp.json`:
```json
{"keyword": "...", "organic": [{"url": "...", "title": "..."}], "paa": ["..."], "aio": null|"...", "has_local_pack": true}
```

**Pułapka:** SERP w Chrome jest **zlokalizowany pod przeglądarkę usera**. Spogle na „wynajem dmuchańców" było w Chrome
na 9. miejscu, w Senuto na 29. **Pozycję bierz z Senuto, skład SERP-u (kto, jaki typ stron) z Chrome.**

## Krok 3 — drabina diagnozy (przerwij po pierwszym trafieniu)

### Szczebel 1 — zły typ strony / zła intencja (z samego SERP-u)
Zaklasyfikuj każdy wynik top10: **oferta firmy** (strona główna / usługa) · **strona miejska** · **cennik** ·
**blog/poradnik** · **marketplace/OLX** · **social (FB)** · **park/miejsce** · **wiki**.
- Top10 = same oferty firm, a user rankuje blogiem/kategorią → **werdykt: potrzebna inna strona, nie poprawka.** STOP.
- Top10 = mieszanka „darmowe miasteczko dmuchańców" (FB), parki, wypożyczalnie (spogle, „dmuchańce warszawa") →
  **intencja rozjechana / sezonowa**; fraza jest warta mniej, niż mówi wolumen. Napisz to. Jedź dalej tylko
  jeśli w top10 jest ≥ 4 stron tego samego typu co strona usera.
- Top10 = strony główne lokalnych firm (10/10 na „rolety kraków") → to walka o **autorytet domeny + GBP**, nie o treść.
  Treść nadal ma znaczenie, ale werdykt musi to powiedzieć wprost.

### Szczebel 2 — co jeszcze jest na tym SERP-ie
- **Local pack** (`has_local_pack`) → dla usługi lokalnej to zwykle ważniejsze niż pozycja 5 vs 12; jeśli usera
  nie ma w local packu — to jest pierwsza rekomendacja, przed treścią.
- **AI Overview**: jest? user cytowany? **Cytowany = zakaz przebudowy** (wolno dokładać, nie przestawiać).
  Brak domeny na liście źródeł **nie dowodzi** braku cytowania (część źródeł za „Pokaż więcej").
- **PAA**: 3–6 pytań = Google publikuje własny fan-out intencji. Sprawdź w kroku 4, czy strona usera na nie odpowiada.

### Szczebel 3 — struktura, mierzona z top10
```
python3 ~/.claude/skills/_senuto-wspolne/crawl_serp.py data/dlaczego-daleko/<slug>/serp.json \
    --mine <URL strony usera> --out data/dlaczego-daleko/<slug>
```
Crawl4AI z `PruningContentFilter` (bez pruningu menu i stopka kłamią w licznikach). Dostajesz tabelę:
słowa · H2 · H3 · listy · wiersze tabel · unikalne liczby · ceny (zł/PLN) · nagłówki-pytania — dla usera i każdej
strony top10 + **medianę**. Porównuj z medianą, **nie z jedynką** (jedynka bywa stroną główną z 300 słów).

**Nie każdy w top10 jest wzorcem** — OLX, FB, strona główna firmy o pasującej nazwie: pomiń w medianie i **powiedz, że pominąłeś**.
Strony z błędem crawla (403, timeout) — wypisz, nie zgaduj ich treści.

Nazwij różnicę konkretnie: nie „za mało treści", tylko „masz 0 wierszy tabeli przy medianie 6 i 1 cenę przy medianie 8".
Jeśli user jest **powyżej** mediany we wszystkim — napisz to; wtedy problem nie leży w treści (autorytet, linki, GBP, wiek strony).

### Szczebel 4 — brakujące podtematy (analiza semantyczna)
```
python3 ~/.claude/skills/_senuto-wspolne/topic_gap.py data/dlaczego-daleko/<slug> --min-share 0.5
```
Sekcje (nagłówek + akapit) wszystkich stron → TF-IDF na n-gramach znakowych (działa po polsku bez lematyzacji,
bez klucza API) → klastry → **podtematy, które ma ≥ 50% top10, a strona usera nie**. Wynik to lista typu
„BRAK: cennik / ceny od…", „BRAK: czas realizacji i montaż", z przykładowymi nagłówkami konkurencji.
To jest jedyna forma „analizy semantycznej", która kończy się listą do dopisania, a nie wykresem.
Progi: `--threshold 0.82` domyślnie; jeśli wychodzi > 40 klastrów z 1 stroną każdy — podnieś do 0.9.

## Krok 4 — werdykt

**Jedno zdanie**, z numerem szczebla, np.:
- „Szczebel 1: na tę frazę Google pokazuje wyłącznie strony główne firm z Krakowa — rankujesz właściwą stroną,
  ale przegrywasz autorytetem i local packiem, nie treścią; treść jest powyżej mediany w 5 z 7 miar."
- „Szczebel 3: masz 2 100 słów przy medianie 900, ale 0 cen przy medianie 7 i 0 tabel przy medianie 5 —
  brakuje Ci cennika, nie tekstu."

Potem **lista braków** (max 5) w kolejności: to, co ma ≥ 70% top10, a Ty nie → PAA bez odpowiedzi → reszta.
Dla każdego: co dopisać (temat + forma: tabela/lista/liczby), gdzie (po którym nagłówku). **Nie pisz treści** —
zakończ: „`/blisko-topu` przygotuje gotowe sekcje do wklejenia".

Zapisz `audyt/dlaczego-daleko-[domena]-[slug]-[data].md`.

## Uczciwość

1. Pozycja z Senuto to jeden pomiar; SERP z Chrome jest zlokalizowany — obie liczby podaj z datą i źródłem.
2. Mediana z 8 stron to rząd wielkości, nie norma.
3. Jeśli szczebel 1 mówi „inna strona", nie dokładaj „a poza tym dopisz 500 słów" — to rozmywa jedyną ważną rzecz.
4. Linków i wieku domeny ten skill nie mierzy — gdy treść jest ≥ mediany, powiedz, że przyczyna leży poza nim.

## Pułapki zaszyte w tym skillu

- Moduł SERP Senuto: `serp_create` → **402 Paywall** mimo `serp_analysis_daily_limit 6000` — limit ≠ dostęp.
- Chrome `javascript_tool` ucina wynik → dwa wywołania (organic / PAA+AIO).
- Playwright: pierwszy crawl bez `playwright install chromium` kończy się `Executable doesn't exist`.
- Crawl4AI: strony z Cloudflare/403 zwrócą `ok: false` — wypisz i pomiń w medianie.
- `journey_stage` z Senuto bywa błędny przy frazach lokalnych — CPC jest lepszym sygnałem intencji zakupowej.
- Firecrawl `/search`, Bright Data, Apify — nie nadają się / wygasłe (patrz `_senuto-wspolne/google-serp-chrome.md`).
