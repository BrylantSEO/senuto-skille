---
name: jedna-strona-czy-dwie
description: >
  Odpowiada na pytanie „czy te frazy to jedna strona, czy kilka — i którą stroną mam na nie odpowiadać?" bez terminala.
  Bierze listę fraz (od usera, z kanibalizacji Senuto albo z fraz jednej przeciążonej strony), sprawdza dla każdej żywe
  wyniki Google (NodesHub MCP, jeśli jest; inaczej Claude in Chrome), czyta intencję z tego, co Google POKAZUJE (nie ze słów),
  łączy frazy w klastry po nakładaniu się top10 i dla każdego klastra rozstrzyga: JEDNA STRONA · ZŁE DOPASOWANIE (rankuje
  główna/blog, wyniki chcą oferty/cennika/strony miejskiej) · KANIBALIZACJA (scal albo rozdziel intencje) · BRAK STRONY.
  Użyj, gdy user pyta „jaka jest intencja tych fraz", „czy X i Y to jedna podstrona", „scalić czy rozbić", „kanibalizacja —
  co z tym zrobić", „rozbudowa serwisu — jakie podstrony". NIE mierzy treści (od tego /dlaczego-daleko).
---

# jedna-strona-czy-dwie (wersja bez terminala)

**Wymagania:** Senuto MCP + źródło wyników Google: **NodesHub MCP** (`serpdata-mcp` w konfiguracji Claude Desktop, klucz z nodeshub.io —
100 tokenów na start; pełne URL-e, bez lokalizacji, + klasyfikator intencji i fan-out) **albo** Claude in Chrome (za darmo, ale wyniki
zlokalizowane pod Ciebie i bez klasyfikatora). Rozsądny zakres: **5–15 fraz**.

## Zasady
1. **Intencję ustala Google, nie słownik.** „dmuchańce warszawa" brzmi jak „wynajem dmuchańców warszawa", a w wynikach to darmowe parki,
   posty FB i kalendarz miejski. Senuto oznacza ją `tofu`, klasyfikator NodesHub (po wynikach) `LOCAL / BOFU / SEASONAL` — drugi ma rację.
2. **Jedna intencja = jedna strona; dwie intencje = dwie strony**, nawet gdy frazy różnią się jednym słowem.
3. **Strony główne lokalnych firm rankują na wszystko** — te same 7 firm na „rolety kraków" i „rolety zewnętrzne kraków", ale drugą frazę
   wygrywają podstronami. Nakładanie się **domen** nic nie mówi; liczą się wspólne wyniki w **top3** i wspólne **podstrony** w top10.

## Krok 0 — skąd frazy (jedno z czterech)
1. **Lista od usera** (3–15).
2. **Kanibalizacja:** `get_cannibalization_keywords domain, country_id: "200"` → frazy z `current_url ≠ previous_url`, oba żywe.
3. **Frazy jednej strony:** `get_positions_data` (`extended`, `limit: 25`, sort po CPC lub searches) → wiersze z tym samym `url.current`
   (strona główna krakowrolety: 46 fraz; strona warszawska spogle: wszystkie ogólnopolskie).
4. **Expander:** NodesHub MCP — fan-out dla seeda (15–20 wariantów z typem). Do klastrowania bierz `specification` (podtemat → kandydat
   na podstronę), `personalized` (miasto), `implicit` (cennik/„najlepsze"); `reformulation` i `entailment` (opinie, kontakt) to frazy do
   wplecenia, nie strony. Wolumeny: Senuto `get_keywords` (baza `"1"`, `match_mode: wide`, do 4 seedów w jednym zapytaniu).

## Krok 1 — wyniki Google per fraza
**NodesHub MCP:** search dla każdej frazy (gl=pl, hl=pl, 20 wyników — tyle samo tokenów co 10, a widać usera na 11–20) + klasyfikator
intencji (`main_intent`, `journey_stage`, `action_type`, `content_timeliness`, `brand_type`). Zapisz per fraza: top10 (pełne URL-e),
pytania PAA, powiązane wyszukania, mapa (nazwy firm), AI + źródła, pozycja i adres usera.
**Chrome (fallback):** `https://www.google.com/search?q=<fraza>&hl=pl&gl=pl` + skrypt z `/dlaczego-daleko` krok 2 (top10, PAA, AI, mapa).
Pamiętaj: wyniki zlokalizowane — na „wynajem dmuchańców" Chrome pokazał SERP warszawski i zlepił frazę z „…warszawa"; NodesHub je rozdzielił.

## Krok 2 — klastry po nakładaniu wyników
Dla każdej pary fraz policz: **wspólne wyniki w top3** i **wspólne podstrony w top10** (adresy inne niż strona główna domeny).
**Ta sama strona**, gdy ≥ 2 wspólne w top3 **lub** ≥ 3 wspólne podstrony. Buduj klastry od frazy o największym wolumenie; dokładaj frazę,
jeśli pasuje do ≥ połowy fraz już w klastrze. Pary z 2 wspólnymi podstronami / 1 w top3 → „na granicy", rozstrzygnij typem stron w top3.
Dla klastra: suma wolumenu, **typ wyników** (udział: oferta główna / podstrona / strona miejska / cennik / blog / marketplace / social / wiki),
cechy (mapa, AI), Twoje strony w klastrze. Przy ≤ 15 frazach robisz to w głowie — tabelę par wpisz do raportu jako dowód.

## Krok 3 — decyzja per klaster
| Sytuacja | Sygnał | Decyzja |
|---|---|---|
| **JEDNA STRONA, dobra** | 1 Twoja strona, jej typ = typ dominujący w wynikach | zostaw; frazy klastra = tytuł/H2; poz. > 10 → `/dlaczego-daleko` |
| **ZŁE DOPASOWANIE** | Twoja strona = główna/blog/kategoria, wyniki = podstrony ofertowe / cennik / miejskie | dedykowana strona typu z wyników; stara linkuje (bez 301 — odpowiada na inne frazy) |
| **KANIBALIZACJA** | ≥ 2 Twoje strony w jednym klastrze | **scal** (301 słabszej do mocniejszej, treść unikalna przenieś), chyba że każda ma własny klaster — wtedy **rozdziel intencje**: inny tytuł/H1/pierwszy akapit, wzajemne linki |
| **BRAK STRONY** | klaster bez Twojej strony, intencja z klientem | jedna nowa strona na klaster, typ z wyników |
| **ROZJECHANA / SEZONOWA** | social + parki + oferty; `SEASONAL`; powiązane „za darmo" | nie przebudowuj; sekcja dla drugiej intencji na końcu; wolumen liczy się ×0,5 |
| **NAWIGACYJNA / CUDZA MARKA / INNY BIZNES** | `BRANDED`, top1 = marka; wyniki = inny typ firmy (agencje eventowe vs wypożyczalnia) | wyrzuć — i napisz dlaczego |

Scalić czy rozdzielić: **scal**, gdy obie strony celują w ten sam klaster i żadna nie ma osobnych fraz w top10; **rozdziel**, gdy każda
ma własny klaster, a Google myli je przez zbliżone tytuły. Przepisanie intencji = tytuł, H1, pierwszy akapit, linkowanie; treść zwykle zostaje.

## Krok 4 — raport `jedna-strona-czy-dwie-[domena]-[data].md`
Werdykt (N fraz → M intencji, ile stron brakuje, kanibalizacja, największa niespodzianka) · **Mapa fraza → klaster → strona** (klaster |
frazy (szukań) | co pokazuje Google (top3) | intencja | Twoja strona (poz.) | decyzja) · **Kanibalizacja: scalić czy rozdzielić** (strony |
klaster | decyzja | jak) · **Nowe strony do zbudowania** (typ z wyników) · **Frazy do wplecenia** (nie osobne strony) · Czego raport nie widzi
(wyniki z jednego dnia; wolumeny to szacunki; klasyfikator to model — przy niezgodzie z typem stron w top3 wierz stronom).

## Przykłady z testów (2026-09-07)
- spogle.pl, 13 fraz → 9 intencji. „agencja eventowa" i „organizacja imprez eventowych" = organizatorzy pełnej obsługi (inny biznes —
  nie budować); „wynajem atrakcji na eventy" = wypożyczalnie (strona główna 17. → wydzielić hub); „dmuchańce warszawa" ≠ „wynajem
  dmuchańców warszawa" (parki vs wypożyczalnie).
- krakowrolety.pl, 9 fraz → 6 intencji, wszystkie obsługiwane stroną główną; Google na każdą pokazuje inne firmy w top3 → brak
  `/plisy-krakow/`, `/zaluzje-krakow/`, `/rolety-zewnetrzne-krakow/`.
