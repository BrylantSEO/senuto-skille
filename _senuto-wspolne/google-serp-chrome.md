---
serwis: Google Search (SERP)
domeny: google.com/search
zweryfikowano: 2026-08-27
---

# Google Search — zbieranie SERP-a przez Chrome MCP

## Kiedy przeglądarka, a kiedy API

**Przeglądarka wygrywa** przy pojedynczej frazie i gdy potrzebujesz **źródeł AI Overview**.
Sprawdzone na „media plan": Chrome dał 6 pytań PAA, pełne adresy podstron i **listę domen
cytowanych w AIO**; NodesHub na tej samej frazie dał 4 pytania, w `url` **tylko domeny główne**
(`https://sempai.pl/`, nie adres artykułu) i `sources: []` przy `source_counts: 0`.

**API wygrywa** przy biegu wsadowym (dziesiątki fraz, cron) — Chrome wymaga człowieka i karty.

**Nie próbuj tych źródeł na polski SERP:** Firecrawl `/v2/search` zwraca wyniki angielskie
mimo `location: "Poland"` oraz `lang`/`country: pl` (dostaniesz coursera.org i hubspot.com
na frazę „media plan"). Bright Data i Apify — zależnie od stanu konta.

## Trasa

`https://www.google.com/search?q=FRAZA&hl=pl&gl=pl` — nawigacja bezpośrednia działa,
nie trzeba wpisywać w pole. Bez `hl`/`gl` dostaniesz język przeglądarki.

## Ekstraktor (javascript_tool) — organic + PAA + AIO

```js
(() => {
  const out = {};
  const org = [];
  document.querySelectorAll('#search a').forEach(a => {
    const h = a.querySelector('h3');
    if (h && a.href && !a.href.includes('google.com')) org.push({url: a.href, title: h.innerText});
  });
  const seen = new Set();
  out.organic = org.filter(o => { const d = new URL(o.url).hostname;
    if (seen.has(d)) return false; seen.add(d); return true; }).slice(0,10);

  const q = new Set();
  document.querySelectorAll('[jsname] [role="heading"], div[data-q], [aria-expanded]').forEach(e => {
    const t = (e.innerText||'').trim();
    if (t.endsWith('?') && t.length < 120 && t.split('\n').length === 1) q.add(t);
  });
  out.paa = [...q];

  const txt = document.body.innerText;
  const i = txt.search(/Przegląd od AI|AI Overview/i);
  out.aio_text = i >= 0 ? txt.slice(i, i + 1500) : null;

  // ŹRÓDŁA AIO: linki POZA #search. Blok AIO stoi nad listą organiczną i jego
  // odnośniki nie należą do #search — to jedyny pewny sposób ich odsiania.
  const src = [], search = document.querySelector('#search');
  document.querySelectorAll('a[href^="http"]').forEach(a => {
    if (search && search.contains(a)) return;
    if (a.href.includes('google.')) return;
    const d = new URL(a.href).hostname.replace('www.','');
    if (!src.includes(d)) src.push(d);
  });
  out.aio_source_domains = src.slice(0,15);
  return JSON.stringify(out).slice(0, 4000);
})()
```

## Rzeczy, których nie widać z ekranu

- **`#search a` z `<h3>` w środku** = wynik organiczny. Bez filtra `h3` złapiesz też linki
  z bloków bocznych i „Podobne wyszukiwania".
- **Dedup po hostname jest konieczny** — Google wypisuje pod jednym wynikiem sitelinki
  prowadzące na tę samą domenę; bez deduplikacji „top10" ma 25 pozycji.
- **Źródeł AIO NIE ma w `#search`.** Selektory typu `[data-attrid*="AIOverview"]` bywają
  zmienne; stabilniejsze jest odsianie linków spoza `#search` (patrz kod wyżej).
- **AIO pokazuje część źródeł dopiero po „Pokaż więcej"** — zebrana lista bywa niepełna.
  Brak domeny na liście **nie dowodzi**, że nie jest cytowana.
- **Kolejność organiczna różni się między biegami** i między Chrome a API (personalizacja,
  lokalizacja). Do porównań bierz zbiór stron, nie dokładne pozycje.
- **Nagłówki PAA doklejają się przy rozwijaniu** — czytaj listę przed klikaniem, inaczej
  złapiesz też pytania z drugiego poziomu.

## Konsument
Skille `/dlaczego-daleko`, `/co-sie-stalo`, `/jedna-strona-czy-dwie` — wynik ekstraktora zapisz jako `serp/<slug>.json` w formacie z `serp_cluster.py` (keyword, organic[{url,title}], paa, aio, has_local_pack).

Skill `/blisko-topu-pro` (`.claude/skills/blisko-topu-pro/`, szczebel 1 w kroku 6a).
Wynik ekstraktora przepakuj w JSON i podaj do `scripts/serp_from_json.py --mine-domain <domena>`,
który od razu orzeka, czy user jest cytowany w AIO.
