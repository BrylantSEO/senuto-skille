---
name: luka-konkurencji
description: >
  Odpowiada na pytanie „kto mnie wyprzedza i NA CZYM?" — bez terminala, tylko Senuto MCP. Dobiera 2–3 realnych konkurentów
  (z Senuto albo wskazanych), wyciąga frazy, na które oni są na 1. stronie, a Ty nie, odsiewa cudze marki, inne miasta,
  inne produkty i ruch bez klienta, i grupuje resztę PO STRONACH konkurenta: „on ma stronę X z 12 frazami kupującymi —
  Ty nie masz odpowiednika". Wynik: 3–7 stron do zbudowania/wzmocnienia z priorytetem P1–P3. Użyj, gdy user pyta „na czym
  wygrywa konkurencja", „jakie frazy ma konkurent, a ja nie", „co mam dobudować", „porównaj mnie z X".
---

# luka-konkurencji (wersja bez terminala)

**Wymagania:** Senuto MCP. **Zużycie:** 1 (dobór) + 1–2 na konkurenta + 0–1 własne = 5–8 zapytań.

## Zasady
1. **Konkurent SEO ≠ konkurent biznesowy; fraza konkurenta ≠ fraza dla Ciebie.** Rollcom rankuje na „firanki kraków" i „rolety łomża" —
   inny produkt, inne miasto. Do raportu trafia tylko fraza, przy której dokończysz *„człowiek, który to wpisuje, może kupić u mnie, bo…"*.
2. **Raport mówi o stronach, nie o frazach.** Laik nie wdroży 37 fraz; wdroży „zbuduj stronę o żaluzjach drewnianych z cennikiem".

## Krok 0 — biznes i zasięg
Zapytaj raz: *„Czym zarabiacie, kto jest klientem i gdzie?"* Zasięg decyduje, czy „rolety wieliczka" to szansa, czy szum.

## Krok 1 — limity (darmowe)
`get_limits`. Potrzebujesz ~8 zapytań `visibility`.

## Krok 2 — dobór konkurentów (1 zapytanie)
`get_competitors domain, country_id: "200", detail_level: "standard", limit: 15`. Pierwszy wiersz = Ty. Pola: `domain, common_keywords, top3, top10, top50, visibility`.
Zostaw 2–4: **sortuj po `common_keywords`**, wyrzuć portale/marketplace'y (wysoka widoczność, mało wspólnych fraz), producentów
ogólnopolskich przy usłudze lokalnej (widoczność 10× Twojej), inne miasta (sprawdź stronę główną), inny model (sklep vs montaż).
**Lista pusta lub < 2 sensowne** (nisze — spogle dostał 1 wiersz i był to portal edukacyjny): nie ponawiaj. Otwórz w Claude in Chrome
Google na 2 główne frazy kupujące usera (albo poproś usera o wklejenie top10) i weź domeny **powtarzające się w obu**. W raporcie: „dobór ręczny".
User wskazał konkurenta → `get_domain_statistics` (1), żeby sprawdzić, czy jest w bazie.

## Krok 3 — frazy konkurentów (1–2 na domenę)
```
get_positions_data  domain: <konkurent>, country_id: "200", detail_level: "standard", limit: 100,
                    order: {prop: "statistics.searches.current", dir: "desc"}
```
Po `searches`, nie po `visibility` (widoczność zwraca tylko top10 konkurenta). `page: 2` tylko, jeśli po odsiewie zostało < 10 kandydatów.
**Nie używaj `get_keywords` z `data_fetch_mode: "url"`** — zwraca 0 i nie ma pozycji. Frazy per strona konkurenta = grupowanie po `url`.
Własne frazy: z `/gdzie-stoje` albo ten sam call na własną domenę.

## Krok 4 — luka + odsiew
**Luka** = konkurent ≤ 10, Ty > 20 albo brak (`position: 51` + pusty `url`). Oboje 11–20 = remis → `/dlaczego-daleko`.
Odsiew (u rollcom.pl z 100 fraz zostało 31): marka konkurenta/cudza · inne miasto poza zasięgiem (zapytaj raz o dojazd) · inny produkt ·
generyk bez lokalizacji przy usłudze lokalnej · serwis/naprawa, gdy user tylko sprzedaje · `url` z „›" lub `/mapa-witryny` (konkurent
**nie ma** strony na ten temat — fraza do wzięcia dedykowaną stroną, nie wzorzec).
Sygnał sprzedażowy (zostaw nawet przy małym wolumenie): miasto/dzielnica, `cennik`, `cena`, `na wymiar`, `montaż`, `wynajem`, produkt + miasto; CPC ≥ 3 zł potwierdza.

## Krok 5 — grupowanie po stronach konkurenta
Dla każdej strony konkurenta: liczba fraz, suma wolumenu, najlepsza pozycja, najwyższe CPC. Sprawdź u usera (z `get_urls` z `/gdzie-stoje`):
**BRAK STRONY** → do zbudowania · **STRONA JEST, NIE RANKUJE** → do wzmocnienia (`/dlaczego-daleko`) · **STRONA GŁÓWNA ROBI ZA WSZYSTKO**
(krakowrolety: 46 fraz na `/`) → wydziel podstronę.
**Priorytet:** P1 = konkurent ≤ 5, Ty brak, ≥ 2 frazy sprzedażowe, temat w ofercie · P2 = konkurent ≤ 10, Ty 20–50 · P3 = jedna fraza / mały wolumen / konkurent rankuje sitemapą lub główną (fraza bezpańska). **3–7 stron.**

## Krok 6 — dlaczego on wygrywa, czego nie kopiować
Jedno zdanie z danych: dedykowana podstrona vs główna · cennik w adresie/tytule (`plisy-krakow-cennik`) · strona miejska · galeria.
Nie wiesz → „sprawdzi to `/dlaczego-daleko`". Nie zalecaj kopiowania treści; zalecaj stronę, która odpowiada na tę samą intencję lepiej.
Konkurent rankujący **stroną główną** na 20–40 fraz = autorytet domeny/wizytówka, nie treść — napisz to.

## Krok 7 — raport `luka-konkurencji-[domena]-[data].md`
Werdykt (kto najbliższy, na jakim typie stron wygrywa, ile stron brakuje) · **Tabela stron** (P | temat/strona | konkurent i jego URL |
frazy kupujące z pozycją konkurenta | Ty | dlaczego on wygrywa) · Co odrzuciłem i dlaczego (3–5) · Czego nie kopiować · Czego raport nie widzi
(jeden pomiar; szacunki; Mapy; [dobór ręczny]).

## Pułapki
`get_competitors` pusty w niszach · `get_positions_data` nie filtruje po frazie/URL — filtrujesz osądem · `url` z „›" = breadcrumb ·
`position: 51` = poza top50 · zawsze `country_id: "200"`.
