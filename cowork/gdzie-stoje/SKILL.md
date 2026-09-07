---
name: gdzie-stoje
description: >
  Raport SEO „od zera" dla osoby nietechnicznej, bez terminala i bez skryptów: wpisujesz domenę i dostajesz po ludzku —
  ile Google Cię pokazuje, które strony na to pracują, jak wypadasz na tle 3–5 konkurentów, 5–8 fraz z klientem tuż pod
  topem WYCENIONYCH W ZŁOTYCH, czy strony nie biją się ze sobą, czy AI Cię cytuje, oraz JEDNĄ rzecz do zrobienia w tym
  tygodniu. Dane tylko z Senuto MCP (Baza 2.0). Użyj, gdy user pyta „jak stoi moja strona w Google", „przeanalizuj moją
  domenę", „od czego zacząć SEO", „gdzie stoję". NIE pisze treści (od tego /blisko-topu) i NIE analizuje konkurenta
  w głąb (/luka-konkurencji).
---

# gdzie-stoje (wersja bez terminala)

**Dla kogo:** właściciel firmy, marketer bez SEO. Raport ma **jedną stronę**, zaczyna się od werdyktu i kończy jedną decyzją.
**Wymagania:** Senuto MCP. Nic więcej — żadnych skryptów, kluczy, instalacji. Działa w Claude Code i Claude Cowork.
**Zużycie:** 7–9 zapytań z `visibility_analysis_queries_per_day` (limit zwykle 400; mimo nazwy odnawia się co ~30 dni).
Zapytania z kroków 2–6 nie zależą od siebie — wyślij je w jednej turze.

## Zasada nadrzędna
**Liczby są tanie, osąd jest drogi.** Senuto zwróci 3 000 fraz; Twoja robota to powiedzieć, które 30 ma znaczenie i dlaczego.
Każda liczba ma być przetłumaczona na skutek dla firmy. Nie wolno: (1) nazywać `visibility` ruchem — to szacunek;
(2) chwalić za frazę bez klienta; (3) wypisać więcej niż 7 rekomendacji.

## Krok 0 — jedno zdanie o biznesie
Zapytaj **raz**: *„Czym zarabiacie, kto jest klientem i gdzie (miasto / cała Polska)?"* Bez odpowiedzi: wnioskuj ze strony głównej
i wpisz na górze raportu jako „Założenie o biznesie". Ustal typ: **usługa lokalna** / **sklep** / **firma-blog ogólnopolski**.

## Krok 1 — limity (darmowe)
`get_limits` → `visibility_analysis_queries_per_day`. Mniej niż 8 do końca okresu → wersja skrócona (kroki 2, 3, 5), napisz to.

## Krok 2 — ile Google Cię pokazuje (1 zapytanie)
`get_domain_statistics domain, country_id: "200"` → `summary.overview`: `top3, top10, top50, visibility`;
`full_statistics.aio_keywords` (frazy z odpowiedzią AI) i `aio_visible_keywords` (w ilu jesteś cytowany); `summary.changes`
= różnica do poprzedniego pomiaru (tylko ostatni krok, nie trend).
> „Google pokazuje Twoją stronę przy **[top50]** zapytaniach, na 1. stronie przy **[top10]**, w top3 przy **[top3]**."
Zawsze `country_id: "200"` — Baza 1.0 pokazuje połowę fraz.

## Krok 3 — skąd ta widoczność (2 zapytania)
**3a. Frazy po widoczności:** `get_positions_data domain, country_id: "200", detail_level: "standard", limit: 30,
order: {prop: "statistics.visibility.current", dir: "desc"}`. Pola: `keyword, position, position_diff, visibility, searches, cpc, difficulty, url`.
Wyłap **artefakty** (z udziałem w widoczności): fraza obok biznesu z ogromnym wolumenem, wpisy obcojęzyczne, fraza
o mieszanej intencji. Marka: poza top3 = alarm nr 1; brak w danych = „nie da się ocenić"; nazwa generyczna = pomiń test.
**3b. Strony:** `get_urls domain, country_id: "200", detail_level: "extended", limit: 20` (**`extended` obowiązkowo** — `standard`
nie ma statystyk). Czytaj `all_urls[].statistics.{visibility,top3,top10,top50}.current`. Policz udział pierwszej strony;
> 50% → „połowa widoczności to jedna strona". Zaklasyfikuj adresy: usługi / blog / słownik / kategorie / produkty.
Adres z „›" = Google pokazuje listing zamiast artykułu → łatwa wygrana linkowaniem.

## Krok 4 — na tle konkurencji (1–3 zapytania)
`get_competitors domain, country_id: "200", detail_level: "standard", limit: 15`. Pierwszy wiersz = Ty. Zostaw 3–5 domen, które
**sprzedają to samo tej samej grupie**: wyrzuć portale, ogólnopolskich producentów przy usłudze lokalnej (widoczność 10×
większa, mało wspólnych fraz), inne miasta. Sortuj po `common_keywords`. **Lista pusta** (nisze) → nie ponawiaj; weź 2–3 domeny
z wyników Google na 2 główne frazy (Claude in Chrome / wklejka usera), dociągnij `get_domain_statistics` (max 3), zaznacz „dobór ręczny".

## Krok 5 — frazy z klientem tuż pod topem, wycenione (1–2 zapytania)
```
get_positions_data  domain, country_id: "200", detail_level: "extended", limit: 25,
                    order: {prop: "statistics.cpc.current", dir: "desc"}          # frazy, za które ktoś płaci
```
`extended` daje per fraza: `statistics.intentions.journey_stage` (tofu/mofu/bofu), `snippets.current` (czy jest `ai_overview`,
`people_also_ask`, `map`), `position.history` (daty → pozycja), `trends.history` (12 mies. wolumenu). **`limit: 25`, nie więcej** —
odpowiedź jest duża (~50 kB). Duża domena (> 500 fraz): drugi przebieg `order: statistics.searches.current`, `standard`, `limit: 60`.

**Filtr biznesowy — trzy sygnały, w tej kolejności:**
1. **Osąd:** dokończ zdanie *„człowiek, który to wpisuje, może u nas kupić, bo…"*. Wyrzuć: literówki („google ether"), generyki
   jednowyrazowe, cudze marki („krakżal", „anwis"), ruch bez klienta („hotel nad morzem" u wypożyczalni), `position: 51` z pustym
   `url` (= poza top50), wolumen < 20.
2. **`journey_stage`:** bofu/mofu zostaje, tofu do kosza — **ale** bywa błędny przy frazach lokalnych i wynajmowych
   („dmuchańce warszawa" = tofu przy CPC 8,64 zł).
3. **CPC:** ≥ 5 zł = reklamodawcy płacą = fraza z klientem, nawet gdy stage mówi tofu. CPC 0 przy frazie jak nazwa firmy = cudza marka.

**Pasmo pozycji:** 4–15; usługa lokalna 4–25 (najcenniejsze frazy „[usługa] [miasto]" wiszą na 2.–3. stronie). Plus 3 największe
z pozycji 16–30 jako „duże, ale dalej".

**Wycena** (złotówki zamiast pozycji):
```
zysk klików/mies. = szukania × (CTR(3) − CTR(teraz))     CTR: 1→27%, 2→15,6%, 3→10,4%, 4→7,5%, 5→5,4%, 6→4%,
wartość zł/mies.  = zysk klików × min(CPC, 60 zł)           8→2,6%, 10→1,9%, 11–15→1,2%, 16–20→0,8%, 21–30→0,4%
```
Przykład: „rolety kraków" 1 300 × (10,4% − 0,4%) × 20,74 zł ≈ 2 700 zł/mies. na 25. miejscu. Podawaj jako rząd wielkości.
**Zsumuj po stronie** (`url`): „3 strony niosą 80% potencjału" — to lista do roboty, nie 40 fraz. Jedna strona główna na
4 tematy (u krakowrolety: rolety, plisy, żaluzje, zewnętrzne) = „wydziel podstrony", nie „popraw główną".

**Kolumna AI:** `snippets` zawiera `ai_overview` → przy tej frazie jest odpowiedź AI. Strona cytowana w AIO = **zakaz przebudowy**
(wolno tylko dokładać). **Mapa:** `get_characteristics_table domain, characteristics: "serp_params", country_id: "200"` (1 zapytanie)
→ jeśli `map` > 30% widoczności (krakowrolety: 39%), pierwsza rekomendacja to wizytówka Google, nie treść.

Wybierz **5–8** fraz: fraza · pozycja (+ historia pierwszy→ostatni pomiar) · pyta/mies. · strona · warte ok. zł · AI · dlaczego warto.
Pokaż też 2–3 odrzucone z powodem. Zakończ: „Dla trzech pierwszych `/blisko-topu` przygotuje gotowy tekst."

## Krok 6 — czy strony biją się ze sobą (1 zapytanie)
`get_cannibalization_keywords domain, country_id: "200", detail_level: "standard"` → `keyword, position, current_url, previous_url,
searches` + `summary.severity`. Senuto pokazuje **zmianę adresu między pomiarami**. Odsiej: stare adresy po przekierowaniu
(poproś usera o sprawdzenie w przeglądarce, czy `previous_url` przekierowuje — jeśli tak, to nie walka, tylko opóźnienie Senuto),
duplikaty techniczne, strony testowe (`/test…/` → posprzątać). Z reszty max 3 po `searches`. `NONE/LOW` → jedno zdanie w „Co już działa".

## Krok 7 — raport
Zapisz `gdzie-stoje-[domena]-[YYYY-MM-DD].md` w folderze projektu. Kolejność sekcji:
1. **Werdykt** (2–3 zdania: skala, największa szansa, największe ryzyko)
2. **Jeśli zrobisz tylko jedną rzecz w tym tygodniu** — co, dlaczego (liczba), 3 kroki, jak sprawdzisz
3. **Ile Google Cię pokazuje** — tabela Ty vs konkurenci (top50 / 1. strona / top3 / wspólne frazy) + zdanie o AI
4. **Co na to pracuje** — proporcja typów stron, koncentracja, marka
5. **Frazy z klientem tuż pod topem (5–8)** — z kolumnami „Warte ok. zł/mies." i „AI"; + „duże, ale dalej"; + odrzucone
6. **Strony, które biją się ze sobą (max 3)**
7. **Co już działa** (3–5)
8. **Czego ten raport nie widzi** — szacunek ≠ ruch; jeden pomiar; Mapy/linki osobno; [dobór ręczny]

Forma: bez „SERP", „CTR", „striking distance" w nagłówkach; liczby zaokrąglone; CPC nie pokazuj (tylko wynik mnożenia); bez obietnic „wzrost o X%".

## Pułapki Senuto
- `country_id: "200"` do pomiaru; `get_keywords/get_questions/get_groups` tylko `"1"`.
- `get_urls standard` nie ma statystyk; `visibility_percent` zawsze 0; `limit` zwraca więcej niż prosisz.
- `get_domain_statistics.changes` = ostatni krok; `get_positions_history_chart` dla Bazy 2.0 → `no_data` (nie wołaj).
- `position: 51` + `url: ""` = poza top50. `position_diff` **dodatni = spadek**.
- `get_competitors` bywa pusty w niszach → dobór ręczny, nie ponawianie.
- `extended` jest ciężkie — `limit: 25`; `standard` nie ma intencji ani AI.
- `journey_stage` myli się na frazach lokalnych/wynajmowych — CPC ≥ 5 zł bije etykietę.
