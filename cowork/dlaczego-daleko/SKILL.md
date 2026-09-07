---
name: dlaczego-daleko
description: >
  Odpowiada na pytanie „na frazę X jestem 25. — DLACZEGO?" bez terminala: Senuto MCP (pozycja, intencja, cechy wyników)
  + Claude in Chrome (żywe wyniki Google i pomiar struktury stron z top10 jednym skryptem w przeglądarce). Drabina diagnozy
  od najtańszej przyczyny: zły typ strony → mapa / AI / pytania → struktura mierzona z realnego top10 (nie z badań) → brakujące
  podtematy. Kończy się JEDNYM zdaniem werdyktu i listą braków. Użyj, gdy user pyta „dlaczego jestem tak nisko", „czemu nie
  rankuję na X", „co ma konkurencja, czego ja nie mam". NIE pisze treści (od tego /blisko-topu).
---

# dlaczego-daleko (wersja bez terminala)

**Wymagania:** Senuto MCP + Claude in Chrome. Zero Pythona — pomiar struktury robi skrypt uruchamiany **w przeglądarce** na każdej
stronie (`javascript_tool`). Jeśli masz NodesHub jako MCP (`serpdata-mcp`) — użyj go do wyników zamiast Chrome (bez lokalizacji).
**Zużycie:** 1–2 zapytania Senuto; Chrome: 1 wyszukanie + ~10 otwartych stron.

## Zasady
1. **Nie zakładaj, że problemem jest długość.** Mierz poprzeczkę z realnego top10 tej frazy. Bardzo często strona usera jest dłuższa
   od jedynki, a przegrywa granulacją, brakiem cen albo tym, że to w ogóle zły typ strony.
2. **Drabina z przerwaniem.** Jeśli na szczeblu 1 wychodzi „w top10 same oferty, a Ty rankujesz blogiem" — nie mierz treści,
   bo żadna poprawka tekstu tego nie naprawi.

## Krok 0
Wejście: domena + **jedna fraza** (+ opcjonalnie URL strony). Sama domena → `/gdzie-stoje`.

## Krok 1 — co mówi Senuto (1–2 zapytania)
`get_positions_data domain, country_id: "200", detail_level: "extended", limit: 25, order: {prop: "statistics.cpc.current", dir: "desc"}`
(albo po `searches`). Znajdź wiersz frazy: pozycja, `position.history` (pierwszy→ostatni), `intentions.journey_stage`, `cpc`, `snippets`
(`ai_overview` / `people_also_ask` / `map`), `url.current`. Brak w 25 → user poza top50 lub fraza poza bazą; jedź dalej z SERP-em.
`journey_stage` bywa błędny lokalnie — CPC ≥ 5 zł = fraza z klientem. Sprawdź, **czy rankuje ta strona, która powinna**.

## Krok 2 — żywe wyniki Google (Chrome)
Otwórz `https://www.google.com/search?q=<fraza>&hl=pl&gl=pl` i uruchom w `javascript_tool` (zwraca top10 + pytania + AI + mapa):
```js
(()=>{const o=[];const s=new Set();document.querySelectorAll('#search a').forEach(a=>{const h=a.querySelector('h3');
if(h&&a.href&&!a.href.includes('google.com')){const u=new URL(a.href);const d=u.hostname.replace('www.','');
if(!s.has(d)){s.add(d);o.push({url:a.href,title:h.innerText.slice(0,60)})}}});
const q=new Set();document.querySelectorAll('[jsname] [role="heading"],div[data-q],[aria-expanded]').forEach(e=>{const t=(e.innerText||'').trim();
if(t.endsWith('?')&&t.length<120&&t.split('\n').length===1)q.add(t)});const t=document.body.innerText;
return JSON.stringify({organic:o.slice(0,10),paa:[...q].slice(0,6),aio:/Przegląd od AI/.test(t),map:/Więcej firm|Więcej miejsc/.test(t)})})()
```
Wynik bywa ucięty przy ~1 500 znakach — jeśli tak, uruchom dwa razy (raz `organic`, raz `paa/aio/map`).
**Pułapka:** Google w Chrome jest zlokalizowany pod Ciebie (spogle: 9. w Chrome, 29. w Senuto). **Pozycja z Senuto, skład wyników z Chrome.**
Zapisz listę top10 do raportu.

## Krok 3 — drabina (przerwij po pierwszym trafieniu)
**Szczebel 1 — typ strony / intencja.** Zaklasyfikuj każdy wynik: oferta firmy (strona główna / usługa) · strona miejska · cennik · blog ·
marketplace/OLX · social (FB) · park/miejsce · wiki.
- Same oferty, a user rankuje blogiem/kategorią → **werdykt: potrzebna inna strona.** STOP.
- Mieszanka (FB „darmowe miasteczko", parki, wypożyczalnie) → intencja rozjechana/sezonowa; fraza warta mniej niż wolumen. Dalej tylko, jeśli ≥ 4 wyniki są tego samego typu co strona usera.
- 10 stron głównych lokalnych firm („rolety kraków") → walka o **autorytet domeny + wizytówkę**, nie o treść; powiedz to wprost.

**Szczebel 2 — co jeszcze jest na tym SERP-ie.** Mapa (`map`) → dla usługi lokalnej ważniejsza niż pozycja 5 vs 12; brak usera w mapie =
pierwsza rekomendacja. AI (`aio`) → cytowany = zakaz przebudowy; brak na liście źródeł nie dowodzi braku cytowania. PAA (3–6 pytań) →
sprawdź w kroku 4, czy strona usera odpowiada.

**Szczebel 3 — struktura, mierzona z top10.** Otwórz **stronę usera i każdą z top10** (pomiń OLX/FB/wiki) i na każdej uruchom:
```js
(()=>{const kill=['nav','header','footer','aside','script','style','form'];document.querySelectorAll(kill.join(',')).forEach(e=>e.remove());
const m=document.querySelector('main')||document.querySelector('article')||document.body;const t=m.innerText||'';
const heads=[...m.querySelectorAll('h2,h3')].map(h=>h.innerText.trim()).filter(Boolean);
return JSON.stringify({url:location.href,words:t.split(/\s+/).filter(Boolean).length,h2:m.querySelectorAll('h2').length,h3:m.querySelectorAll('h3').length,
li:m.querySelectorAll('li').length,tr:m.querySelectorAll('tr').length,prices:(t.match(/\d[\d\s.,]*\s?(zł|PLN)\b/gi)||[]).length,
faq:heads.filter(h=>h.endsWith('?')).length,img:m.querySelectorAll('img').length,heads:heads.slice(0,30)})})()
```
Zbierz do tabeli: słowa · H2 · H3 · listy · wiersze tabel · ceny · FAQ · zdjęcia — dla usera i każdej strony; policz **medianę** top10
(bez OLX/FB/strony-wizytówki z 200 słów — i powiedz, że pominąłeś). Porównuj z medianą, nie z jedynką.
Nazwij różnicę konkretnie: nie „za mało treści", tylko „0 wierszy tabeli przy medianie 6, 1 cena przy medianie 8". User powyżej mediany
we wszystkim → problem nie leży w treści (autorytet, linki, wizytówka, wiek strony).

**Szczebel 4 — brakujące podtematy.** Z pola `heads` (nagłówki) każdej strony top10 ułóż listę podtematów; zaznacz te, które ma **≥ 5 z 10 stron**,
i sprawdź, czy strona usera je ma (po sensie, nie po słowie). To jest lista „dopisz sekcję o…". Do tego pytania PAA bez odpowiedzi na stronie usera.

## Krok 4 — werdykt
**Jedno zdanie z numerem szczebla**, np. „Szczebel 3: masz 2 100 słów przy medianie 900, ale 0 cen przy medianie 7 i 0 tabel przy medianie 5 —
brakuje Ci cennika, nie tekstu." Potem **lista braków (max 5)**: co dopisać (temat + forma: tabela/lista/liczby), gdzie. Nie pisz treści —
„`/blisko-topu` przygotuje gotowe sekcje". Zapisz `dlaczego-daleko-[domena]-[fraza]-[data].md`.

## Uczciwość
Pozycja z Senuto (data), SERP z Chrome (zlokalizowany) — podaj oba. Mediana z 8 stron to rząd wielkości. Jeśli szczebel 1 mówi „inna strona",
nie dokładaj „a poza tym dopisz 500 słów". Linków i wieku domeny ten skill nie mierzy — gdy treść ≥ mediany, powiedz, że przyczyna leży poza nim.
