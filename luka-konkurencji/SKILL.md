---
name: luka-konkurencji
description: >
  Odpowiada na pytanie „kto mnie wyprzedza i NA CZYM?". Bierze domenę, dobiera 2–3 realnych konkurentów
  (z Senuto MCP albo wskazanych ręcznie), wyciąga frazy, na które oni są na pierwszej stronie, a Ty nie,
  odsiewa wszystko, co nie przyniesie klienta (cudze marki, generyki, inne miasta, ruch bez sprzedaży)
  i grupuje resztę PO STRONACH konkurenta: „on ma stronę X, która przynosi mu 12 fraz kupujących — Ty nie masz
  odpowiednika". Wynik to lista 3–7 stron do zbudowania lub wzmocnienia z priorytetem. Czysty Senuto MCP,
  zero skryptów. Użyj, gdy user pyta „na czym wygrywa konkurencja", „jakie frazy ma konkurent, a ja nie",
  „co mam dobudować", „content gap", „porównaj mnie z X". NIE robi audytu jednej strony (od tego
  /dlaczego-daleko) ani raportu startowego (od tego /gdzie-stoje).
---

# luka-konkurencji

**Dla kogo:** właściciel firmy, który wie, kto jest jego konkurentem w Google (albo chce się dowiedzieć),
i chce usłyszeć **co konkretnie ma tamten, czego on nie ma** — w postaci stron do zrobienia, nie listy 400 fraz.

**Wymagania:** Senuto MCP. Nic więcej.
**Zużycie:** 1 zapytanie na dobór konkurentów + 1–2 na każdego konkurenta + 0–1 na własną domenę
(jeśli nie masz jej z `/gdzie-stoje`). Typowo **5–8 zapytań** `visibility_analysis_queries_per_day`.

> Wersja 1.0 (2026-09-07) — przetestowana na krakowrolety.pl (usługa lokalna, 3 konkurentów z listy Senuto)
> i spogle.pl (lista konkurentów w Senuto **pusta** — dobór ręczny z SERP-u). Kształty pól zweryfikowane na żywo.

---

## Zasada nadrzędna

**Konkurent SEO ≠ konkurent biznesowy, a fraza konkurenta ≠ fraza dla Ciebie.** Senuto pokaże, że rollcom.pl
rankuje na „firanki kraków" i „rolety łomża" — pierwsze to inny produkt, drugie to inne miasto. Content gap
bez odsiewu jest listą cudzych błędów, nie Twoich szans. Do raportu trafia tylko fraza, przy której
dokończysz zdanie: *„człowiek, który to wpisuje, może kupić u mnie, bo…"*.

Druga zasada: **raport mówi o stronach, nie o frazach.** Laik nie wdroży „37 fraz do poprawy". Wdroży
„zbuduj stronę o żaluzjach drewnianych z cennikiem, bo konkurent ma taką i ona przynosi mu 9 fraz kupujących".

---

## Krok 0 — jedno zdanie o biznesie + zasięg

Jeśli nie wiesz z kontekstu, zapytaj **raz**: *„Czym zarabiacie, kto jest klientem i gdzie (miasto / cała Polska)?"*
Zasięg jest tu ważniejszy niż w innych skillach — decyduje, czy „rolety wieliczka" to szansa, czy szum.
Tryb bez rozmowy: strona główna przez `WebFetch`, wniosek wpisany jako **„Założenie o biznesie"**.

## Krok 1 — limity (darmowe)

`get_limits` → `visibility_analysis_queries_per_day`. Potrzebujesz ok. 8. Jeśli mniej — zrób wersję
z jednym konkurentem i napisz to w raporcie.

## Krok 2 — dobór konkurentów (1 zapytanie)

```
get_competitors  domain, fetch_mode: "topLevelDomain", country_id: "200", detail_level: "standard", limit: 15
```
Pierwszy wiersz to własna domena (`is_main_domain: true`). Pola: `domain, common_keywords, top3, top10, top50, visibility`.

**Odsiew — zostaw 2–3 domeny, maksymalnie 4:**
| Wyrzuć | Jak poznać |
|---|---|
| portale / marketplace'y | wikipedia, olx, allegro, ceneo, facebook — wysoka `visibility`, niski `common_keywords` |
| producenci ogólnopolscy przy usłudze lokalnej | `visibility` 10× większa od Twojej, `common_keywords` małe (krakowrolety: skalmar.pl 3 243 vs 151) |
| inne miasto | sprawdź `WebFetch` strony głównej — 0 zapytań |
| inny model biznesu | sklep internetowy vs montaż na miejscu — inne frazy, inny klient |

**Sortuj po `common_keywords`, nie po `visibility`.** Ten, kto ma z Tobą najwięcej wspólnych fraz, jest najbliższym
konkurentem w Google — nawet jeśli jest mniejszy.

**Lista pusta albo < 2 sensowne domeny** (nisze; spogle.pl dostał 1 wiersz i był to portal o różnorodności
kulturowej) — **nie ponawiaj** z `extended` ani Bazą 1.0. Weź 2 główne frazy kupujące usera, wpisz w Google
(Chrome MCP albo WebSearch, 0 zapytań Senuto) i zapisz domeny, które **powtarzają się w obu SERP-ach**.
W raporcie zaznacz: „dobór ręczny z wyników Google, bez danych o wspólnych frazach".

Jeśli user wskazał konkurenta — bierz go bez dyskusji, ale sprawdź `get_domain_statistics` (1 zapytanie),
czy w ogóle jest w bazie.

## Krok 3 — frazy konkurentów (1–2 zapytania na domenę)

Dla każdego konkurenta:
```
get_positions_data  domain: <konkurent>, fetch_mode: "topLevelDomain", country_id: "200",
                    detail_level: "standard", limit: 100,
                    order: {prop: "statistics.searches.current", dir: "desc"}
```
Pola: `keyword, position, position_diff, visibility, searches, cpc, difficulty, url`.

**Dlaczego po `searches`, nie po `visibility`:** sortowanie po widoczności zwraca tylko frazy z top10
konkurenta (poza top10 `visibility` = 0), a sortowanie po wolumenie daje przekrój całości. Przy konkurencie
> 300 fraz dociągnij `page: 2` **tylko jeśli** po odsiewie z kroku 4 zostało < 10 kandydatów.

**Nie używaj `get_keywords` z `data_fetch_mode: "url"`** — zwraca 0 wyników (jedzie po bazie 1.0) i nie ma pozycji.
Frazy per strona konkurenta bierzesz z tego samego `get_positions_data`, grupując po polu `url`.

Własne frazy: jeśli masz świeży `/gdzie-stoje` — użyj jego danych. Jeśli nie — ten sam call na własną domenę.

## Krok 4 — luka + odsiew (tu jest cała wartość)

**Luka** = fraza, na której konkurent jest **≤ 10**, a Ty **> 20 albo Cię nie ma** (brak w Twojej liście
lub `position: 51` z pustym `url`). Frazy, gdzie oboje jesteście 11–20, to nie luka — to remis, idzie do `/dlaczego-daleko`.

**Odsiew — bez niego lista jest w 70% szumem** (zmierzone na rollcom.pl: z 100 fraz po odsiewie zostało 31):
| Wyrzuć | Przykład z testu |
|---|---|
| marka konkurenta lub cudza | `rollcom`, `roltis`, `anwis rolety`, `selt markiza`, `orlita kraków`, `krakżal` |
| inne miasto / region poza zasięgiem | `rolety wieliczka`, `rolety myślenice`, `rolety łomża` — chyba że user tam jeździ, **zapytaj raz** |
| inny produkt | `firanki kraków`, `zasłony na wymiar`, `bramy przemysłowe`, `karnisze` — jeśli user tego nie sprzedaje |
| generyk bez lokalizacji przy usłudze lokalnej | `veranda`, `refleksol`, `markiza koszowa` — ogólnopolski SERP, przegrasz z producentami |
| serwis/naprawa, gdy user tylko sprzedaje | `naprawa rolet`, `dorabianie pilotów` |
| `position: 51` u konkurenta | to „poza top50", nie 51. |
| `url` z „›" lub `/mapa-witryny` | breadcrumb / mapa strony — Google pokazuje sitemapę, bo konkurent **nie ma** dedykowanej strony; to nie wzorzec do kopiowania, to sygnał, że fraza jest do wzięcia |

**Sygnał sprzedażowy** (zostaw, nawet przy małym wolumenie): fraza zawiera miasto/dzielnicę, `cennik`, `cena`,
`na wymiar`, `montaż`, `wynajem`, `producent`, nazwę produktu + miasto. CPC ≥ 3 zł = reklamodawcy już płacą
za ten klik — dobry potwierdzacz, ale nie jedyny (u lokalnych usług CPC bywa 0 przy frazach ewidentnie kupujących).

## Krok 5 — grupowanie po stronach konkurenta

Dla każdego konkurenta zgrupuj ocalałe frazy po `url`. Dla każdej strony policz: liczba fraz, suma wolumenu,
najlepsza pozycja, najwyższe CPC. Następnie sprawdź, **czy user ma odpowiednik**:
- **BRAK STRONY** — w `get_urls` usera (z `/gdzie-stoje`) nie ma strony o tym temacie → „do zbudowania";
- **STRONA JEST, ALE NIE RANKUJE** — user ma URL o tym temacie, ale na te frazy jest > 20 → „do wzmocnienia",
  handoff do `/dlaczego-daleko`;
- **STRONA GŁÓWNA ROBI ZA WSZYSTKO** — user rankuje na te frazy stroną główną (krakowrolety: 46 fraz w top50
  na `/`), a konkurent dedykowaną podstroną → „wydziel podstronę".

**Priorytet** (nie sam wolumen):
- **P1** — konkurent ≤ 5, Ty brak, ≥ 2 frazy sprzedażowe, temat w ofercie usera → strona do zbudowania w tym miesiącu
- **P2** — konkurent ≤ 10, Ty 20–50 → wzmocnić istniejącą
- **P3** — jedna fraza, mały wolumen, albo konkurent rankuje sitemapą/stroną główną (fraza „bezpańska")

Weź **3–7 stron**. Nie więcej — nikt więcej nie zbuduje.

## Krok 6 — czego NIE kopiować

Dla każdej strony P1 napisz jedno zdanie, **dlaczego konkurent wygrywa** (z danych, nie z domysłu):
dedykowana podstrona vs strona główna · cennik w URL-u/tytule (`plisy-krakow-cennik`) · strona miejska
(`rolety-wieliczka`) · galeria realizacji. Jeśli nie wiesz — napisz „nie wiadomo z tych danych, sprawdzi to `/dlaczego-daleko`".
**Nie zalecaj kopiowania treści.** Zalecaj stronę, która odpowiada na tę samą intencję lepiej (cennik z widełkami,
czas realizacji, zdjęcia z miasta).

## Krok 7 — raport

Zapisz do `audyt/luka-konkurencji-[domena]-[YYYY-MM-DD].md`. Struktura:

```markdown
# Na czym wygrywa konkurencja — [domena] vs [k1], [k2], [k3] — [data]

> **Założenie o biznesie / zasięg:** …  [dobór konkurentów: z Senuto po wspólnych frazach / ręczny]

## Werdykt
[2–3 zdania: kto jest najbliższym konkurentem, na jakim typie stron wygrywa, ile stron brakuje userowi]

## Strony do zbudowania lub wzmocnienia (3–7)
| P | Temat / strona | Konkurent i jego URL | Frazy kupujące (poz. konkurenta) | Ty | Dlaczego on wygrywa |
[P1 → P3; „Ty": brak / poz. X na URL / strona główna]

## Co odrzuciłem i dlaczego (3–5 przykładów)
[inne miasto, cudza marka, inny produkt — to uczy usera czytać własne dane]

## Czego nie kopiować
[…]

## Czego ten raport nie widzi
- pozycje z jednego pomiaru Senuto (data), bez trendu;
- „wolumen" to szacunek, „widoczność" to nie ruch;
- Mapy Google / local pack — dla usług lokalnych to często główne pole walki, tu go nie ma;
- [jeśli dobór ręczny] brak danych o wspólnych frazach.
```

Reguły formy jak w `/gdzie-stoje`: bez żargonu w nagłówkach, liczby zaokrąglone, CPC nie pokazuj (użyj do selekcji).

## Pułapki Senuto zaszyte w tym skillu

- `get_competitors` bywa **pusty lub bez sensu** dla nisz (spogle: 1 wiersz, portal edukacyjny) → dobór ręczny z SERP-u, nie ponawianie.
- `get_positions_data` **nie filtruje po frazie ani po URL-u** — filtrujesz osądem po pobraniu; dlatego sort po `searches`, limit 100.
- `get_keywords` `data_fetch_mode: url` → 0 wyników (baza 1.0). Nie używać.
- `url` z „›" = breadcrumb; `/mapa-witryny`, `/sitemap` jako rankujący URL = konkurent nie ma strony na ten temat → fraza do wzięcia dedykowaną stroną.
- `position: 51` + `url: ""` = poza top50.
- Konkurent lokalny często rankuje **stroną główną** na 20–40 fraz (rollcom.pl: „rolety kraków" poz. 2 na `/`) — wtedy „dlaczego wygrywa" to autorytet domeny/GBP, nie treść; napisz to, nie zalecaj „napisz dłuższą stronę główną".
- Zawsze `country_id: "200"`.
