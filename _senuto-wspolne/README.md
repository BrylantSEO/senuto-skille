# Pięć skilli Senuto MCP (+NodesHub) dla osoby bez SEO — rodzina i wspólny moduł

| # | Skill | Pytanie właściciela | Wejście | Zależności | Zapytania Senuto |
|---|---|---|---|---|---|
| 1 | `/gdzie-stoje` (v3) | „Jak stoję i co nisko wisi?" | domena | Senuto | 6–9 |
| 2 | `/luka-konkurencji` | „Kto mnie wyprzedza i na czym?" | domena (+konkurenci) | Senuto (+Chrome przy pustej liście) | 5–8 |
| 3 | `/dlaczego-daleko` | „Dlaczego na X jestem 25.?" | domena + fraza | Senuto + Chrome MCP + crawl4ai | 1–2 |
| 4 | `/co-sie-stalo` | „Spadło mi — co się stało?" | domena (+fraza/data) | Senuto (+Chrome) | 3–5 |
| 5 | `/jedna-strona-czy-dwie` | „Te frazy to jedna strona czy kilka? Scalić czy rozbić?" | lista fraz / kanibalizacja / seed | **NodesHub** (6 tok./fraza) + Senuto | 1–3 + ~100 tokenów NH |

Kolejność naturalna: 1 → (2 lub 4) → 5 (architektura: która strona na co) → 3 → `/blisko-topu` (pisze gotowy tekst).

## Wspólny moduł: filtr biznesowy
Każdy skill najpierw odsiewa frazy bez klienta. Trzy źródła sygnału, w tej kolejności:
1. **osąd** — „człowiek, który to wpisuje, może u nas kupić, bo…" (cudze marki, generyki, inne miasto, inny produkt);
2. **`intentions.journey_stage`** z `detail_level: extended` (bofu/mofu/tofu) — **bywa błędny** przy frazach lokalnych i wynajmowych;
3. **CPC** — ≥ 5 zł bije etykietę `tofu`; 0 zł przy frazie brzmiącej jak nazwa firmy = cudza marka.
Wycena: `szukania × (CTR(3) − CTR(teraz)) × min(CPC, 60)` — złotówki zamiast pozycji.

## Skrypty (Python 3.12, bez kluczy API)
- `senuto_extended.py` — tabela z odpowiedzi `extended` (~100 kB): stage, CPC, AIO/PAA/map, historia, wins/losses; `--bofu`, `--drops`, `--gains`.
- `crawl_serp.py` — Crawl4AI (długość z `fit_markdown`) + surowy HTML (struktura: H2/H3/listy/tabele/liczby/ceny/FAQ/img) dla usera i top10; mediana. `--from-cache` przelicza bez crawla.
- `topic_gap.py` — sekcje H2/H3 z HTML → TF-IDF char 3–5 → klastry → podtematy, które ma ≥ 50% top10, a user nie.
- `nodeshub_serp.py` — wsadowe SERP-y z NodesHub (`/v1/search` num=20, `/v1/intent-classifier`, `/v1/query-fanout`) → `serp/*.json`; klucz w `.env` DD.
- `serp_cluster.py` — klastry intencji po nakładaniu SERP-ów (≥2 wspólne w top3 lub ≥3 wspólne podstrony w top10; strony główne nie liczą się), typ SERP-u, decyzja JEDNA/ZŁE DOPASOWANIE/KANIBALIZACJA/BRAK.

## Pułapki zmierzone przy budowie (2026-09-07)
- `PruningContentFilter` **wycina nagłówki** (35 H2 → 1). Struktura zawsze z HTML, długość z pruningu.
- Filtr klas po podciągu (`widget`, `menu`) wycina cały Elementor — dopasowanie po całym tokenie klasy.
- Moduł SERP Senuto: `serp_create` → 402 Paywall mimo limitu 6000 — SERP przez Chrome MCP.
- Chrome SERP jest zlokalizowany (spogle 9. vs Senuto 29.) — pozycja z Senuto, skład SERP-u z Chrome.
- `get_competitors` bywa pusty dla nisz (spogle) — dobór ręczny z dwóch SERP-ów.
- `journey_stage` „tofu" na „dmuchańce warszawa" (CPC 8,64) — wierz CPC; klasyfikator NodesHub (po SERP-ie) dał LOCAL/BOFU/SEASONAL — lepiej.
- Chrome SERP zlokalizowany zlepia frazy ogólnopolskie z miejskimi („wynajem dmuchańców" + „…warszawa"); NodesHub je rozdziela — do klastrowania tylko NodesHub.
- NodesHub 402 = brak tokenów, nie zły klucz; klucz DD w `.env` projektu (stary w `Plan_zycia/.env` miał 0 tokenów).

Testy: `audyt/senuto-skille/` (10 raportów: spogle.pl, krakowrolety.pl). Dane: `data/senuto-skille/`, `data/dlaczego-daleko/`, `data/co-sie-stalo/`, `data/jedna-strona/`.
