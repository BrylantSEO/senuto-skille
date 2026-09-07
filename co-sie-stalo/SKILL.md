---
name: co-sie-stalo
description: >
  Odpowiada na pytanie „spadło mi — co się stało i co robić?". Bierze domenę (opcjonalnie frazę, stronę lub datę),
  wyciąga z Senuto MCP (Baza 2.0, historia pozycji z 4–12 punktów) frazy, które straciły najwięcej, odsiewa spadki
  bez znaczenia biznesowego i dla każdego realnego spadku rozstrzyga, która z TRZECH przyczyn zaszła:
  (A) sam się przesunąłeś — zmiana adresu, przekierowanie, kanibalizacja; (B) SERP się zmienił — AI Overview,
  local pack, sezonowa zmiana intencji; (C) ktoś Cię wyprzedził — kto i jaką stroną. Każda przyczyna ma inną
  reakcję, w tym „nic nie rób". Czysty Senuto MCP + opcjonalnie Chrome MCP do SERP-u. Użyj, gdy user pyta
  „dlaczego spadłem", „co się stało z pozycjami", „ruch leci w dół", „straciłem pozycję na X", „czy to update".
  NIE jest raportem startowym (/gdzie-stoje) ani analizą jednej frazy w głąb (/dlaczego-daleko).
---

# co-sie-stalo

**Dla kogo:** właściciel, który zobaczył spadek na wykresie i chce wiedzieć **czy to jego wina, wina Google,
czy konkurent** — bo od tego zależy, czy ma coś robić, i co.

**Wymagania:** Senuto MCP. Chrome MCP opcjonalnie (dla przyczyny B/C). Skrypt pomocniczy
`~/.claude/skills/_senuto-wspolne/senuto_extended.py` (czyta duże odpowiedzi `extended`; można bez niego, ręcznie).
**Zużycie:** 3–5 zapytań `visibility_analysis_queries_per_day`.

> Wersja 1.0 (2026-09-07) — przetestowana na spogle.pl („dmuchańce warszawa" 5→20, przyczyna A+B) i krakowrolety.pl
> („rolety zewnętrzne kraków" 19→38, „montaż rolet kraków" 2→14). Historia w Bazie 2.0: spogle 12 punktów
> (co 4 dni, od 22.07), krakowrolety 5 punktów (co 10 dni) — gęstość zależy od domeny.

---

## Zasada nadrzędna

**Trzy różne przyczyny, trzy różne reakcje — i jedna z nich to „nie ruszaj".** Najczęstszy błąd właściciela po spadku:
cofnąć ostatnią zmianę (np. przekierowanie 301), która była dobra i właśnie się „przełącza" w Google. Drugi:
przepisać stronę, która spadła, bo sezon zmienił intencję frazy — i stracić ją na dobre.

Druga zasada: **spadek na frazie bez klienta to nie problem.** Spadek `zabawy integracyjne dla dzieci` 22→43
u wypożyczalni dmuchańców jest nieistotny; spadek `dmuchańce warszawa` 5→20 jest. Filtr biznesowy przed diagnozą.

---

## Krok 0 — co spadło według usera

Zapytaj **raz**: *„Co zauważyłeś — ruch, konkretna fraza, konkretna strona? Od kiedy?"* Jeśli user ma GSC/GA — poproś
o datę i stronę; Senuto ma tylko pozycje, nie ruch. Bez odpowiedzi: jedź po całej domenie.

## Krok 1 — limity (darmowe) + stan (1 zapytanie)

`get_limits`. Potem:
```
get_domain_statistics  domain, country_id: "200"
```
`summary.changes` (top3/top10/top50/visibility z różnicą do poprzedniego pomiaru) + `aio_keywords` /
`aio_visible_keywords`. **To tylko ostatni krok**, nie trend — spogle: `-4 (-0.96%)` w top10 wygląda niewinnie,
a pod spodem jedna fraza przychodowa straciła 15 pozycji. Nie kończ na tym.

## Krok 2 — największe spadki (1–2 zapytania)

```
get_positions_data  domain, country_id: "200", detail_level: "extended", limit: 50,
                    order: {prop: "statistics.position.diff", dir: "desc"}
```
`position.diff` dodatni = spadek. `extended` daje `position.history` (daty → pozycja), `changes.wins/losses`,
`url.current/previous/is_change`, `intentions`, `snippets`, `trends.history` (12 mies. wolumenu). Odpowiedź ~100 kB
→ zapisz do pliku i:
```
python3 ~/.claude/skills/_senuto-wspolne/senuto_extended.py positions.json --drops --min-searches 30
```
`--drops` = ostatni punkt historii ≥ 3 pozycje gorszy od pierwszego. Kolumny: poz · hist (pierwszy→ostatni) · w/l · stage · szuk · cpc · AIO · PAA · url.

Drugi przebieg, jeśli domena jest duża (> 500 fraz) i pierwszy zwrócił same frazy blogowe:
```
order: {prop: "statistics.cpc.current", dir: "desc"}   # frazy, za które ktoś płaci = frazy z klientem
```

**Odsiew** (jak w `/gdzie-stoje`): cudze marki, generyki, ruch bez klienta, `position: 51` z pustym `url` (wypadła
z top50 — to spadek, ale bez adresu nie zdiagnozujesz; zostaw w tabeli z adnotacją). Zostaw **3–7 fraz**, które
(1) mają klienta, (2) straciły ≥ 3 pozycje, (3) wolumen ≥ 30. Frazy z tej samej strony grupuj — spadek strony, nie frazy.

## Krok 3 — trzy przyczyny, w tej kolejności

### A. Sam się przesunąłeś (dane Senuto, 1 zapytanie)
Sprawdź dla każdej frazy:
- `url.is_change = 1` / `url.previous ≠ url.current` → Google przełączył adres. Jeśli `previous` robi **301** na
  `current` (`curl -o /dev/null -w "%{http_code}" -s <previous>`, 0 zapytań) → **to przekierowanie się przełącza;
  reakcja: NIE cofać, poczekać 4–8 tyg., sprawdzić, czy linki wewnętrzne i sitemap wskazują nowy adres.**
- `get_cannibalization_keywords domain, country_id: "200", detail_level: "standard"` → fraza na liście z `current_url`
  ≠ `previous_url`, oba żywe (200) → **dwie Twoje strony biją się o frazę; reakcja: jedna główna, druga linkuje albo
  301.** Uwaga: `current_url` w `test2-2/`, `/?p=`, `/kategoria/` = strona robocza/kategoria przejęła frazę → posprzątać
  (noindex/usunięcie), nie „poprawiać treści".
- **Sam coś zmieniłeś?** — zapytaj usera o zmiany na stronie w oknie ±7 dni od pierwszego spadku w historii
  (nowy szablon, zmiana tytułu, migracja). To najczęstsza przyczyna i Senuto jej nie widzi.

### B. SERP się zmienił (Senuto + Chrome)
- `snippets.current` zawiera `ai_overview` → AIO nad wynikami zjada 30–40% klików pozycji 2–5. Jeśli AIO pojawił się
  niedawno, pozycja mogła zostać, a ruch spaść. Cytowany → zakaz przebudowy.
- `snippets` zawiera `map` → local pack; dla usługi lokalnej **pozycja organiczna 5 vs 12 znaczy mniej niż obecność
  w mapie**. Sprawdź `get_characteristics_table characteristics: "serp_params"` — u krakowrolety `map` = 39% widoczności.
- **Sezon**: `trends.history` (12 punktów wolumenu) — jeśli szczyt był 2–3 miesiące temu, część spadku to sezon.
- **Zmiana intencji**: żywy SERP w Chrome (`_senuto-wspolne/google-serp-chrome.md`) — zaklasyfikuj top10. „dmuchańce warszawa"
  we wrześniu 2026: 3 posty FB o **darmowych** miasteczkach dmuchańców, 2 parki, 4 wypożyczalnie → Google zmienił
  frazę z „wynajmę" na „gdzie pójść z dzieckiem". **Reakcja: nie przebudowywać strony pod nową intencję** (straciłbyś
  frazy wynajmowe); poczekać na sezon albo dołożyć akapit dla drugiej intencji na końcu.

### C. Ktoś Cię wyprzedził (Chrome)
Z żywego SERP-u: kto jest **teraz** nad userem, jaką stroną (oferta / cennik / blog / marketplace). Jeśli to nowa
dedykowana strona konkurenta (np. `plisy-krakow-cennik`) → handoff do `/dlaczego-daleko` na tę frazę.
Jeśli nad userem jest OLX / FB / portal — to nie „konkurent", to zmiana SERP-u (B).

**Przypadek D — artefakt pomiaru:** historia ma dziurę (`has_serp: false`), fraza skacze 5→20→6 co pomiar
(`wins` ≈ `losses`, np. `piana party` 4/4) → **niestabilny SERP, nie spadek.** Napisz to i nie rekomenduj niczego.

## Krok 4 — raport

Zapisz `audyt/co-sie-stalo-[domena]-[YYYY-MM-DD].md`:

```markdown
# Co się stało z [domena] — [data]

## Werdykt
[2–3 zdania: co realnie spadło (frazy z klientem), która przyczyna dominuje, czy trzeba coś robić]

## Spadki, które mają znaczenie (3–7)
| Fraza | Było → jest (daty) | Strona | Przyczyna (A/B/C/D) | Dowód | Co robić |

## Spadki, które NIE mają znaczenia
[2–4 przykłady: fraza blogowa, cudza marka, niestabilny SERP — z powodem]

## Czego NIE robić
[np. nie cofać 301 z 29.07; nie przepisywać strony pod sezonową intencję]

## Jak sprawdzisz za 4 tygodnie
[konkretne frazy + oczekiwany kierunek; Rank Tracker Senuto: rt_get_position_data daje pomiar dzienny,
 jeśli user ma projekt — 27 z 1000 fraz zajętych u DD, jest miejsce]

## Czego ten raport nie widzi
- ruch (GSC/GA) — Senuto widzi pozycje co 4–10 dni;
- zmiany na stronie, o których user nie powiedział;
- linki przychodzące i kary ręczne.
```

## Pułapki zaszyte w tym skillu

- `get_domain_statistics.changes` = ostatni krok pomiaru, nie trend; `get_positions_history_chart` dla Bazy 2.0 → `no_data`.
- Historia jest **tylko w `extended`**; gęstość punktów zależy od domeny (co 4 dni vs co 10 dni).
- `position.diff` dodatni = spadek (odwrotnie niż intuicja); sort `desc` daje największe spadki.
- `journey_stage` bywa błędny przy frazach lokalnych/wynajmowych — CPC ≥ 5 zł traktuj jako frazę z klientem mimo `tofu`.
- Kanibalizacja pokazuje **zmianę adresu w czasie**, nie dwie pozycje naraz; 301 na `previous_url` = nie kanibalizacja.
- SERP w Chrome jest zlokalizowany — do „kto jest nad Tobą" wystarczy, do pozycji nie.
- Zawsze `country_id: "200"`.
