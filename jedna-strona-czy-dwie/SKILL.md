---
name: jedna-strona-czy-dwie
description: >
  Odpowiada na pytanie „czy te frazy to jedna strona, czy kilka — i którą stroną mam na nie odpowiadać?".
  Bierze listę fraz (od usera, z kanibalizacji Senuto, z fraz jednej strony albo rozszerzoną fan-outem NodesHub),
  pobiera dla każdej żywy SERP z NodesHub (pełne URL-e, PAA, local pack, AIO, related), klasyfikuje intencję po tym,
  co Google POKAZUJE (nie po słowach), klastruje frazy po nakładaniu się top10 i dla każdego klastra rozstrzyga:
  JEDNA STRONA (masz właściwą) · ZŁE DOPASOWANIE (rankuje strona główna/blog, SERP chce oferty/cennika/strony
  miejskiej → dedykowana strona) · KANIBALIZACJA (dwie Twoje strony na jednej intencji → scal albo rozdziel intencje)
  · BRAK STRONY. Keyword expander w bonusie. Użyj, gdy user pyta „jaka jest intencja tych fraz", „czy X i Y to
  jedna podstrona", „które frazy na jedną stronę", „scalić czy rozbić", „kanibalizacja — co z tym zrobić",
  „rozbudowa serwisu — jakie podstrony", „jak wyglądają SERP-y na…". NIE pisze treści i NIE mierzy poprzeczki
  treści (od tego /dlaczego-daleko).
---

# jedna-strona-czy-dwie

**Dla kogo:** właściciel, który ma 3–30 fraz o podobnym brzmieniu („organizacja imprez eventowych" / „agencja
eventowa" / „wynajem atrakcji na eventy") i nie wie, czy to jedna strona, trzy strony, ani jak wyglądają na nie
wyniki Google. Albo ma z `/gdzie-stoje` listę kanibalizacji i pyta „scalić czy rozdzielić?".

**Wymagania:** NodesHub API (`NODESHUB_API_KEY` w `.env`; 1 token/SERP, +5 za klasyfikator intencji, 7,5 za fan-out).
Senuto MCP opcjonalnie (wolumeny, CPC, lista kanibalizacji, frazy jednej strony). Fallback SERP: Chrome MCP (`_senuto-wspolne/google-serp-chrome.md`) — wtedy bez klasyfikatora i z SERP-em zlokalizowanym pod przeglądarkę. Skrypty:
`~/.claude/skills/_senuto-wspolne/nodeshub_serp.py`, `serp_cluster.py`.
**Koszt typowy:** 15 fraz × (1 + 5) ≈ 90 tokenów NodesHub + 1 fan-out ≈ 100 tokenów; Senuto 1–3 zapytania.

> Wersja 1.0 (2026-09-07) — przetestowana na spogle.pl (13 fraz eventowych) i krakowrolety.pl (9 fraz).

---

## Zasada nadrzędna

**Intencję ustala Google, nie słownik.** „dmuchańce warszawa" brzmi jak „wynajem dmuchańców warszawa", a w SERP-ie
to darmowe parki dmuchańców, posty na FB i kalendarz miejski — Google uznał, że to zapytanie „gdzie pójść z dzieckiem".
Senuto oznacza tę frazę jako `tofu`, klasyfikator NodesHub (po SERP-ie) jako `LOCAL / VISIT_IN_PERSON / BOFU / SEASONAL`
— drugi ma rację, bo patrzy na wyniki, nie na frazę.

Druga zasada: **jedna intencja = jedna strona; dwie intencje = dwie strony — nawet jeśli frazy różnią się jednym słowem.**
Trzecia: **strony główne lokalnych firm rankują na wszystko** — nakładanie się domen nie dowodzi tej samej intencji;
liczą się wspólne wyniki w top3 i wspólne dedykowane podstrony w top10.

---

## Krok 0 — skąd frazy (jedno z czterech wejść)

1. **User podaje listę** (3–30 fraz). Najczęstsze.
2. **Kanibalizacja z Senuto:** `get_cannibalization_keywords domain, country_id: "200"` → frazy, gdzie `current_url ≠ previous_url`
   i oba żywe (nie 301). To gotowa lista pytań „scalić czy rozdzielić".
3. **Frazy jednej strony:** `get_positions_data` (extended, sort CPC lub searches) → filtr po `url.current` = strona, która
   „robi za wszystko" (u krakowrolety strona główna rankuje na 46 fraz; u spogle strona warszawska na wszystkie ogólnopolskie).
4. **Expander:** `nodeshub_serp.py --expand "<seed>"` → fan-out 15–20 wariantów z typem (`specification` = podtemat →
   kandydat na podstronę; `personalized` = miasto; `implicit` = cennik/„najlepsze"; `entailment` = opinie/kontakt/portfolio;
   `reformulation` = ta sama intencja innymi słowami → nie osobna strona). Z fan-outu bierz do klastrowania tylko
   `specification` + `personalized` + `implicit`, resztę zapisz jako „frazy do wplecenia".
   Wolumeny dopnij z Senuto `get_keywords` (baza 1.0, `match_mode: wide`, 1 zapytanie na 4 seedy).

Zapisz frazy do `data/jedna-strona/<domena>/frazy.txt`. Jeśli masz z Senuto — dopisz w plikach `searches` i `cpc`
(skrypt zachowuje te pola przy pobieraniu).

## Krok 1 — SERP-y i intencja (NodesHub, 6 tokenów/fraza)

```
python3 ~/.claude/skills/_senuto-wspolne/nodeshub_serp.py --out data/jedna-strona/<domena> --mine <domena> \
        --file data/jedna-strona/<domena>/frazy.txt --intent
```
Per fraza dostajesz `serp/<slug>.json`: top20 (pełne URL-e, `num=20` żeby złapać pozycje 11–20 usera), PAA, related
searches, local pack (nazwy firm), AIO + źródła, `my_url`/`my_pos`, `intent.classifications` (main_intent, journey_stage,
action_type, content_timeliness, brand_type). Skrypt nie pobiera ponownie plików ze źródłem `nodeshub` — `--force` wymusza.

Bez tokenów (402): Chrome MCP z ekstraktorem z playbooka; pliki w tym samym formacie; brak klasyfikatora — intencję
oceniasz z typów stron (krok 2) i z `intentions` Senuto (`extended`), pamiętając o jego błędach.

## Krok 2 — klastrowanie po nakładaniu SERP-ów

```
python3 ~/.claude/skills/_senuto-wspolne/serp_cluster.py data/jedna-strona/<domena> --mine <domena>
```
Reguła „ta sama strona": **≥ 2 wspólne wyniki w top3** albo **≥ 3 wspólne dedykowane podstrony w top10** (strony główne
się nie liczą — patrz zasada 3). Dla każdego klastra: suma wolumenu, **typ SERP-u** (udział: oferta główna / podstrona /
strona miejska / cennik / blog / marketplace / social / wiki), cechy (mapa, AIO), Twoje strony w klastrze, decyzja.
Dodatkowo dwie listy: **„ten sam rynek, osobne strony"** (te same firmy, inne podstrony → u siebie też rozdziel) i
**„pary na granicy"** (osąd ręczny — sprawdź, czy top3 to ten sam typ strony).

## Krok 3 — decyzja per klaster (tu jest osąd)

| Sytuacja | Sygnał | Decyzja |
|---|---|---|
| **JEDNA STRONA, dobra** | 1 Twoja strona w klastrze, jej typ = typ dominujący w SERP-ie | zostaw; frazy klastra to jej tytuł/H2; jeśli poz. > 10 → `/dlaczego-daleko` |
| **ZŁE DOPASOWANIE** | Twoja strona = główna/blog/kategoria, SERP = podstrony ofertowe / cennik / strony miejskie | **dedykowana strona** o typie z SERP-u; stara linkuje do nowej (bez 301 — stara odpowiada na inne frazy) |
| **KANIBALIZACJA** | ≥ 2 Twoje strony w jednym klastrze (albo Senuto: `current_url` ↔ `previous_url`) | **scal**: 301 słabszej (mniej fraz, mniej linków) do mocniejszej, treść unikalna przenieś; **chyba że** obie strony są potrzebne na inne frazy — wtedy **rozdziel intencje**: każda dostaje inny tytuł/H1 pod inny klaster i linkuje do drugiej |
| **BRAK STRONY** | klaster bez Twojej strony, intencja z klientem | jedna nowa strona na klaster; typ z SERP-u (cennik? miejska? oferta?) |
| **INTENCJA ROZJECHANA / SEZONOWA** | SERP = social + parki + oferty; `content_timeliness: SEASONAL`; related „za darmo" | nie przebudowuj; sekcja dla drugiej intencji na końcu istniejącej strony; wolumen liczy się ×0,5 |
| **NAWIGACYJNA / CUDZA MARKA** | `brand_type: BRANDED`, top1 = marka | wyrzuć |

**Kiedy scalić, a kiedy rozdzielić (kanibalizacja):** scal, gdy obie strony celują w **ten sam klaster** i żadna nie ma
osobnych fraz w top10. Rozdziel, gdy każda ma **własny klaster** w kroku 2 (np. „imprezy integracyjne warszawa" vs
„team building warszawa" — różne SERP-y), a Google myli je tylko dlatego, że mają zbliżone tytuły. Przepisanie intencji =
nowy tytuł, H1, pierwszy akapit i linkowanie wewnętrzne; treść pod spodem zwykle zostaje.

## Krok 4 — raport

Zapisz `audyt/jedna-strona-czy-dwie-[domena]-[YYYY-MM-DD].md`:

```markdown
# Jedna strona czy dwie — [domena] — [data]
> Wejście: [lista usera / kanibalizacja Senuto / frazy strony X / fan-out „seed"] · SERP: NodesHub, [data] · intencja: klasyfikator NodesHub

## Werdykt
[2–3 zdania: ile klastrów z N fraz, ile stron brakuje, gdzie kanibalizacja, największa niespodzianka intencji]

## Mapa: fraza → klaster → strona
| Klaster | Frazy (szukań) | Co pokazuje Google | Intencja | Twoja strona (poz.) | Decyzja |

## Kanibalizacja: scalić czy rozdzielić
| Strony | Klaster | Decyzja | Jak (301 / nowy tytuł / linkowanie) |

## Nowe strony do zbudowania (typ z SERP-u)
## Frazy do wplecenia (nie osobne strony): reformulation/entailment z fan-outu, related searches
## Czego ten raport nie widzi
- SERP z jednego dnia; wolumeny to szacunki Senuto; klasyfikator to model — przy niezgodzie z typem stron w top3 wierz stronom.
```

## Pułapki zmierzone przy budowie

- **Chrome pokazuje SERP zlokalizowany** — na „wynajem dmuchańców" (ogólnopolskie) Chrome dał SERP warszawski i zlepił
  frazę z „wynajem dmuchańców warszawa"; NodesHub dał SERP ogólnopolski (olx, megaland, dmuchancelublin) i rozdzielił je.
  Do klastrowania **tylko NodesHub** (albo wklejka z trybu incognito bez lokalizacji).
- Klastrowanie po **domenach** zlewa wszystko w lokalnych niszach (te same 7 firm na „rolety kraków" i „rolety
  zewnętrzne kraków"); po **URL-ach z wyłączeniem stron głównych** rozdziela poprawnie.
- `journey_stage` Senuto vs klasyfikator NodesHub: przy niezgodzie wierz NodesHub (patrzy na SERP), a obu — typom stron w top3.
- `num=20` kosztuje tyle samo co 10 — zawsze bierz 20, żeby widzieć usera na 11–20.
- Fan-out zwraca też warianty bez wolumenu i bez sensu biznesowego („agencja eventowa praca") — filtruj osądem, dopnij wolumen z Senuto.
- NodesHub 402 = zero tokenów, nie błąd klucza; klucz czytany z `.env` w katalogu roboczym lub wyżej.
