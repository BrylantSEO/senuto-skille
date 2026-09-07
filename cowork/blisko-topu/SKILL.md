---
name: blisko-topu
description: Odpowiada na pytanie „jestem na 12. miejscu i co dalej?" (bez terminala, tylko Senuto MCP). Bierze domenę, wyciąga z Senuto MCP frazy, na których strona jest blisko topu, odsiewa te, które nie przyniosą klienta, i dla 3 najlepszych zwraca GOTOWY materiał do wklejenia — nowy tytuł, opis i brakujące sekcje treści — wraz z szacunkiem, ile klików i złotych da awans. Użyj, gdy user pyta „co poprawić na stronie", „gdzie jestem blisko top3", „na co się teraz skupić w SEO", „mam pozycje i nie wiem, co z nimi zrobić", „quick winy SEO", „striking distance". NIE służy do pisania nowego artykułu od zera ani do analizy konkurencji na całą domenę.
---

# blisko-topu

**Problem, który rozwiązuje:** każde narzędzie SEO mówi „jesteś na 12. miejscu". Żadne nie mówi,
czy to blisko, czy warto, i co dokładnie dopisać. Ten skill kończy się **tekstem do wklejenia**,
nie tabelą.

**Wymagania:** podpięty Senuto MCP. Nic więcej — bez skryptów, bez kluczy API, bez instalacji.

---

## Zasada nadrzędna

Nie szukasz fraz **blisko topu**. Szukasz fraz, które **(1) mogą przynieść klienta** i przy okazji
**(2) są blisko**. Odwrotna kolejność to najczęstszy błąd: lista „pozycje 4–20 posortowane po
wolumenie" jest w 80% śmieciem i właśnie dlatego nikt z niej nie korzysta.

Twoja robota w tym skillu to **osąd**, nie liczenie. Senuto policzy wszystko; tylko Ty odróżnisz
frazę „media plan" (klient szuka usługi) od frazy „google ether" (ktoś szuka Google Earth
i trafił na stronę o E-E-A-T).

---

## Krok 0 — Ustal, czym jest ten biznes

Zanim cokolwiek pobierzesz, ustal **jedno zdanie: na czym ta firma zarabia i kto jest jej
klientem.** Jeśli user tego nie podał — zapytaj, jednym pytaniem. To jedyne pytanie w całym
skillu i bez niego cała reszta jest zgadywanką.

Zapisz to zdanie. Do niego przykładasz każdą frazę w kroku 3.

## Krok 1 — Sprawdź limity (darmowe, nie zużywa nic)

```
get_limits
```

Skill zużywa **2–4 zapytania** z `visibility_analysis_queries_per_day` (limit zwykle 400/dzień)
i 0–3 z `serp_analysis_daily_limit` (zwykle 6000/dzień). Jeśli `visibility` ma mniej niż 4
pozostałe — powiedz to po ludzku („dzisiejszy limit Senuto jest na wyczerpaniu, odnowi się za X
godzin") i przerwij. Nie próbuj obchodzić limitu.

## Krok 2 — Pobierz dwa przekroje

**Zawsze `country_id: "200"`** (baza 2.0). Baza 1.0 pokazuje mniej więcej połowę fraz i zaniża
obraz. To nie jest opcja do przemyślenia — to domyślna wartość.

**Przekrój A — „co już prawie działa" (pozycje 4–10):**
```
get_positions_data
  domain: <domena>
  fetch_mode: "topLevelDomain"
  country_id: "200"
  detail_level: "standard"
  limit: 30
  order: { prop: "statistics.visibility.current", dir: "desc" }
```
Frazy poza top10 mają `visibility: 0`, więc to sortowanie wydobywa dokładnie pasmo 1–10.
Pozycje 1–3 odrzucasz (tam nie ma czego wygrywać).

**Przekrój B — „druga strona Google" (pozycje 11–20):**
```
get_positions_data
  domain: <domena>
  fetch_mode: "topLevelDomain"
  country_id: "200"
  detail_level: "standard"
  limit: 60
  order: { prop: "statistics.searches.current", dir: "desc" }
```
Zostawiasz tylko wiersze z `position` w zakresie 11–20.

Jeśli po odsiewie z kroku 3 zostało mniej niż 8 kandydatów — dociągnij `page: 2` przekroju B.
Nie rób tego „na zapas".

> **Dlaczego `standard`, a nie `extended`:** `standard` daje wszystko, czego potrzebujesz do
> decyzji (`keyword`, `position`, `position_diff`, `searches`, `cpc`, `difficulty`, `url`)
> w jednej ósmej objętości. `extended` dokłada `intentions` (tofu/mofu/bofu) i `snippets`
> (m.in. `ai_overview`) — sięgnij po niego **tylko** przy finalnej trójce, jeśli musisz
> rozstrzygnąć wątpliwość, i wtedy z `limit: 20`.

## Krok 3 — Odsiew (tu jest cała wartość)

Przejdź kandydatów jeden po drugim i **wyrzuć** wszystko, co pasuje do poniższych. Przy każdej
odrzuconej frazie zapisz jednozdaniowy powód — pokażesz to userowi, bo to często najciekawsza
część raportu.

| Wyrzuć | Jak rozpoznać | Przykład z życia |
|---|---|---|
| **Literówki i pomyłki** | fraza brzmi jak coś innego niż treść strony | `google ether`, `google ea`, `is google earth` (165 tys. wyszukań!) trafiają na stronę o **E-E-A-T**. To ludzie szukający **Google Earth**. Zero szans, zero wartości. |
| **Jednowyrazowe generyki** | 1 słowo, ogromny wolumen, rozjechana intencja | `marketing`, `performance`, `seo`, `ar`, `ctr`, `branded`, `growth` |
| **Cudze marki** | nazwa czyjegoś produktu | `mailchimp`, `jasper ai`, `google analytics` — nie przejmiesz, choćbyś stanął na głowie |
| **Twoja własna marka** | nazwa firmy usera | `double digital` — to nie szansa. Ale jeśli jesteś na niej **poza top3, to alarm** — zgłoś osobno |
| **Ruch bez klienta** | pasuje do treści, nie pasuje do biznesu | agencja marketingowa rankująca na `papiery wartościowe`, `podaż co to`, `efekt dunninga krugera` — ruch jest, klienta nie będzie |
| **`position: 51` z pustym `url`** | wartownik „poza top50", nie „51. miejsce" | `ctr` poz. 51, `url: ""` — fraza wypadła z widoczności, to nie jest striking distance |
| **`url` bez ukośnika / z „›"** | Senuto zwrócił breadcrumb, nie adres | `double-digital.pl › Blog/` — zaznacz jako dane do sprawdzenia, nie licz |

**Zostaw** frazy, przy których potrafisz dokończyć zdanie: *„człowiek, który to wpisuje, może
u nas kupić, bo …"*. Jeśli nie potrafisz — wyrzuć.

## Krok 4 — Policz, ile wart jest awans

Dla każdej ocalałej frazy policz zysk z awansu **na pozycję 3** (nie na 1 — 1. miejsce to obietnica
bez pokrycia).

**Krzywa CTR** (uśrednienie sześciu publicznych badań, 2026):

| Pozycja | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11–15 | 16–20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CTR | 27% | 15,6% | 10,4% | 7,5% | 5,4% | 4,0% | 3,2% | 2,6% | 2,2% | 1,9% | ~1,2% | ~0,8% |

```
zysk_klikow  = searches × (CTR(3) − CTR(pozycja_teraz))
wartosc_zl   = zysk_klikow × min(cpc, 60)
```

**Trzy poprawki, bez których liczba kłamie:**

1. **Ucinaj CPC na 60 zł.** Senuto potrafi zwrócić 703 zł za `yt ads`, 440 zł za
   `google adsense adsense`, 275 zł za `ile kosztuje reklama na youtube`. To błąd danych, nie
   złoto. Bez tego capa jedna fraza zdominuje cały ranking.
2. **Jest AI Overview → pomnóż przez 0,65.** Na SERP-ach z AIO pozycje 2–5 tracą 33–38% klików.
   Sprawdzasz to `detail_level: "extended"` → `snippets.current` zawiera `ai_overview`.
   Jeśli nie sprawdzałeś — napisz wprost, że nie sprawdzałeś.
3. **`visibility` z Senuto to nie ruch.** To estymacja (top10 × wolumen × CTR). Nigdy nie
   podawaj jej jako „tylu masz odwiedzających".

**Wysiłek** (im niżej, tym drożej):
- pozycja 4–7 + KD < 50 → **mała poprawka**, 30–60 min
- pozycja 8–10 albo KD 50–65 → **rozbudowa strony**, pół dnia
- pozycja 11–20 albo KD > 65 → **przebudowa albo nowa strona**, 2+ dni

**Ranking:** `wartosc_zl ÷ wysiłek`. Nie sam wolumen. Nigdy sam wolumen.

## Krok 5 — Wybierz 5, opisz 3

Pokaż **piątkę** w tabeli (fraza · pozycja · strona · ile klików/mies. dołoży awans · ile to warte
· ile roboty). Do dalszej pracy weź **trzy pierwsze**. Więcej nikt nie wdroży.

## Krok 6 — Dla każdej z trójki: dlaczego tam jesteś

Potrzebujesz trzech rzeczy: **czy na tym SERP-ie jest AI Overview**, **co jest w top3**
i **co ma Twoja strona**.

### 6a. Najpierw AI Overview — bo potrafi odwołać całą robotę

Sprawdź, czy fraza ma AI Overview i **czy strona usera jest w nim cytowana** (lista źródeł AIO).

- **Jest AIO, user NIE jest cytowany** → prognozę klików mnożysz przez 0,65 i mówisz to wprost.
- **Jest AIO, user JEST cytowany** → **zakaz przebudowy strony.** Struktura, którą ma, jest
  właśnie tym, co Google cytuje; przepisanie jej to ryzyko utraty najcenniejszego miejsca na
  ekranie w zamian za kilka pozycji. Wolno Ci wtedy **dokładać** sekcje wzmacniające dokładnie
  to, co AIO cytuje — nigdy przestawiać ani skracać istniejących.

To jest najważniejsza reguła w tym skillu i najczęściej pomijana: **pozycja nie jest już
najcenniejszą walutą na SERP-ie.**

### 6b. Top3 i porównanie treści

**Ścieżka A — moduł SERP Senuto** (jeśli masz narzędzia `serp_*` — są w oficjalnym serwerze
`mcp.senuto.com`, limit zwykle 6000/dzień i zwykle nietknięty):
```
serp_create   → zleć analizę SERP dla frazy
serp_check    → poczekaj na gotowość
serp_get_report → lista wyników z top10
get_url_sections → struktura sekcji stron konkurencji (nagłówki, bloki)
```
To jest ścieżka domyślna: dane z tego samego źródła co reszta i bez dodatkowych narzędzi.

**Ścieżka B — bez modułu SERP:** poproś usera, żeby wpisał frazę w Google i wkleił **3 pierwsze
linki**. To dosłownie 15 sekund i działa zawsze. Nie udawaj, że znasz top3, jeśli go nie
pobrałeś.

Następnie `WebFetch` na: 3 strony konkurencji + **stronę usera z kolumny `url`**. Z każdej wyciągnij
tylko: tytuł, nagłówki H2/H3, przybliżoną długość, obecność tabeli / FAQ / cennika / konkretnych
liczb.

**Porównaj i nazwij różnicę.** Nie „popraw treść", tylko: *„wszyscy trzej z top3 mają sekcję
z widełkami cenowymi i tabelę porównawczą. Ty masz akapit o firmie i 700 słów przy ich 2100."*

**Dwa błędy, których nie wolno zrobić na tym kroku:**

- **Nie zakładaj, że problemem jest długość.** Sprawdź. Bardzo często strona usera jest
  **dłuższa** od jedynki, a różnica leży w granulacji (ile adresowalnych nagłówków) albo
  w jednym brakującym ujęciu. „Dopisz treści" wtedy szkodzi.
- **Nie każdy w top3 jest wzorcem.** Na frazie „media plan" trzecie miejsce zajmuje
  `mediaplan.com.pl` — strona firmy o tej nazwie, nie materiał na temat. Porównuj się z tymi
  wynikami, które odpowiadają na to samo pytanie; resztę pomiń i **powiedz, że pominąłeś**.
- **Jeśli czegoś nie ma nikt w top10** (np. tabeli) — to nie jest luka do wyrównania, tylko
  wolne miejsce do zajęcia. Zaznacz to osobno, bo to najtańsza przewaga w całym zestawieniu.

## Krok 7 — Oddaj gotowy materiał

Dla każdej z trzech fraz napisz **plik `poprawki-<slug>.md`** zawierający:

1. **Nowy tytuł strony (title)** — gotowy, do skopiowania, ≤ 60 znaków, z frazą.
2. **Nowy opis (meta description)** — gotowy, ≤ 155 znaków.
3. **2–3 sekcje do dopisania — NAPISANE, nie opisane.** Pełny tekst z nagłówkiem H2. To jest
   sedno skilla. „Dodaj sekcję o cenach" to porada. Gotowa sekcja o cenach to robota.
4. **Gdzie to wkleić** — po którym istniejącym nagłówku.
5. **Czego NIE ruszać** — jeśli coś już działa, powiedz to wprost.

Na koniec, w czacie, **trzy zdania**: co robisz w pierwszej kolejności, ile to zajmie, po czym
poznasz, że zadziałało (i **kiedy** — realnie 4–8 tygodni, nie „od razu").

---

## Uczciwość — cztery zdania, których nie wolno pominąć

1. **Nie obiecuj pozycji.** Podajesz, ile *warta byłaby* poprawa, a nie że nastąpi.
2. **Liczby to rząd wielkości.** Krzywa CTR to średnia z badań, a nie Twoja branża.
3. **Senuto widzi swoją bazę fraz, nie całą prawdę** — długi ogon Twojej strony może w niej nie
   istnieć, choć rankuje. Do mierzenia efektu konkretnej zmiany właściwym narzędziem jest
   **Google Search Console**, nie Senuto.
4. **Jeśli po odsiewie nic sensownego nie zostało — powiedz to.** „Masz 3000 fraz, ale wśród
   pozycji 11–20 nie ma ani jednej, na której klient by u Ciebie kupił" to pełnoprawny,
   wartościowy wynik. Wtedy właściwym następnym krokiem jest napisanie czegoś nowego, a nie
   poprawianie starego.

## Pułapki Senuto zaszyte w tym skillu

- `country_id: "200"` do **pomiaru**; `get_keywords` / `get_questions` / `get_groups` obsługują
  **tylko bazę 1.0** — gdybyś ich potrzebował, przełącz na `"1"`.
- `position: 51` + `url: ""` = **poza top50**, nie pozycja 51.
- `detail_level: "standard"` **nie zawiera** `intentions` ani `snippets` — po `ai_overview`
  sięgasz do `extended`.
- CPC bywa absurdalne (setki złotych) — zawsze cap.
- `get_limits` jest darmowe. Wywołuj bez wahania; wszystko inne zużywa dzienny limit.
