---
name: co-sie-stalo
description: >
  Odpowiada na pytanie „spadło mi — co się stało i co robić?" bez terminala, tylko Senuto MCP (+ opcjonalnie Claude in Chrome).
  Wyciąga frazy, które straciły najwięcej (Baza 2.0 ma historię pozycji), odsiewa spadki bez znaczenia biznesowego i dla każdego
  realnego spadku rozstrzyga jedną z trzech przyczyn: (A) sam się przesunąłeś — zmiana adresu, przekierowanie, kanibalizacja;
  (B) SERP się zmienił — AI, mapa, sezon, zmiana intencji; (C) ktoś Cię wyprzedził. Każda ma inną reakcję, w tym „nic nie rób".
  Użyj, gdy user pyta „dlaczego spadłem", „ruch leci w dół", „straciłem pozycję na X", „czy to update".
---

# co-sie-stalo (wersja bez terminala)

**Wymagania:** Senuto MCP. Claude in Chrome opcjonalnie (przyczyny B/C). **Zużycie:** 3–5 zapytań.

## Zasady
**Trzy przyczyny, trzy reakcje — jedna z nich to „nie ruszaj".** Najczęstszy błąd: cofnąć dobre przekierowanie, które właśnie się
„przełącza" w Google. Drugi: przepisać stronę, bo sezon zmienił sens frazy — i stracić ją na dobre.
**Spadek na frazie bez klienta to nie problem.** Filtr biznesowy przed diagnozą.

## Krok 0
Zapytaj raz: *„Co zauważyłeś — ruch, fraza, strona? Od kiedy? Co zmieniałeś na stronie w ostatnich 4 tygodniach?"* Ostatnie pytanie
jest najważniejsze — Senuto nie widzi Twoich zmian.

## Krok 1 — stan (1 zapytanie)
`get_limits`, potem `get_domain_statistics domain, country_id: "200"` → `summary.changes` (tylko ostatni krok!) + `aio_keywords`.
Spogle: „−4 na 1. stronie (−0,96%)" wyglądało niewinnie, a pod spodem fraza przychodowa straciła 15 pozycji. Nie kończ tu.

## Krok 2 — największe spadki (1–2 zapytania)
```
get_positions_data  domain, country_id: "200", detail_level: "extended", limit: 25,
                    order: {prop: "statistics.position.diff", dir: "desc"}      # diff dodatni = SPADEK
```
Z każdego wiersza czytaj: `statistics.position.history` (daty → pozycja; pierwszy i ostatni punkt), `position.changes.wins/losses`,
`url.current / previous / is_change`, `intentions.journey_stage`, `snippets.current` (`ai_overview`, `map`, `people_also_ask`),
`trends.history` (12 miesięcy wolumenu), `cpc`, `searches`. **`limit: 25`** — odpowiedź jest duża.
Domena > 500 fraz i same frazy blogowe → drugi przebieg `order: statistics.cpc.current` (frazy, za które ktoś płaci).
**Odsiew:** cudze marki, generyki, ruch bez klienta, `position: 51` z pustym `url` (wypadła z top50 — zostaw w tabeli z adnotacją).
Zostaw **3–7 fraz**: mają klienta (bofu/mofu albo CPC ≥ 5 zł — CPC bije błędne `tofu`), straciły ≥ 3 pozycje, wolumen ≥ 30.
Frazy z tej samej strony grupuj.

## Krok 3 — trzy przyczyny, w tej kolejności
**A. Sam się przesunąłeś** (Senuto + 1 zapytanie)
- `url.is_change = 1` → Google przełączył adres. Poproś usera, by otworzył `url.previous` w przeglądarce: **przekierowuje na nowy? → to
  przekierowanie się przełącza; NIE cofać, poczekać 4–8 tyg., sprawdzić menu/stopkę/sitemap.**
- `get_cannibalization_keywords domain, country_id: "200"` → fraza z `current_url ≠ previous_url`, oba żywe → **dwie Twoje strony
  o jedną frazę; jedna główna, druga linkuje albo przekierowanie.** `current_url` typu `/test…/`, `/kategoria/`, `?p=` = strona robocza/kategoria
  przejęła frazę → posprzątać, nie „poprawiać treści".
- Zmiany usera w oknie ±7 dni od pierwszego spadku w `history` (szablon, tytuł, migracja) — najczęstsza przyczyna.

**B. SERP się zmienił** (Senuto + Chrome)
- `snippets` ma `ai_overview` → odpowiedź AI zjada 30–40% klików pozycji 2–5; pozycja mogła zostać, ruch spaść. Cytowany → zakaz przebudowy.
- `snippets` ma `map` → dla usługi lokalnej obecność w mapie znaczy więcej niż 5. vs 12. miejsce (`get_characteristics_table serp_params`:
  krakowrolety `map` = 39% widoczności).
- **Sezon:** `trends.history` — szczyt 2–3 mies. temu = część spadku to sezon.
- **Zmiana intencji:** otwórz frazę w Google (Claude in Chrome, `hl=pl&gl=pl`) i zaklasyfikuj top10. „dmuchańce warszawa" we wrześniu:
  3 posty FB o **darmowych** miasteczkach, 2 parki, 4 wypożyczalnie → Google zmienił frazę z „wynajmę" na „gdzie pójść". **Reakcja:
  nie przebudowywać strony** (stracisz frazy wynajmowe); poczekać na sezon lub dodać akapit dla drugiej intencji na końcu.

**C. Ktoś Cię wyprzedził** (Chrome) — kto jest **teraz** nad Tobą i jaką stroną (oferta / cennik / blog / OLX). Nowa dedykowana strona
konkurenta → `/dlaczego-daleko`. OLX/FB/portal nad Tobą = to B, nie C.

**D. Artefakt** — `wins ≈ losses` (np. 4/4), pozycja skacze 5→17→8 co pomiar → niestabilny SERP, nie spadek. Nie rekomenduj niczego.

## Krok 4 — raport `co-sie-stalo-[domena]-[data].md`
Werdykt (co realnie spadło, która przyczyna dominuje, czy trzeba coś robić) · **Spadki, które mają znaczenie** (fraza | było→jest z datami |
strona | przyczyna A/B/C/D | dowód | co robić) · **Spadki bez znaczenia** (2–4 z powodem) · **Czego NIE robić** · **Jak sprawdzisz za 4 tygodnie**
(frazy + kierunek; Rank Tracker Senuto `rt_get_position_data` = pomiar dzienny, jeśli user ma projekt) · Czego raport nie widzi (ruch, zmiany
na stronie, linki; gęstość historii: spogle co 4 dni, krakowrolety co 10).

## Pułapki
`changes` = ostatni krok, nie trend · historia tylko w `extended` · `position.diff` dodatni = spadek · `journey_stage` myli się lokalnie —
CPC rozstrzyga · kanibalizacja = zmiana adresu w czasie, nie dwie pozycje naraz; przekierowanie na `previous_url` = nie kanibalizacja ·
Chrome pokazuje SERP zlokalizowany — do „kto nad Tobą" wystarczy, do pozycji nie · `country_id: "200"`.
