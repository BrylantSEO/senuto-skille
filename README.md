# Skille Senuto MCP dla osoby bez SEO — pakiet

Pięć skilli + `/blisko-topu` (cel handoffu — pisze gotowy tekst) + wspólny moduł. Kopia robocza do dystrybucji (oryginały działają z `.claude/skills/`; ten folder to
paczka do skopiowania do `~/.claude/skills/` u innej osoby lub do repo kursu). Zbudowane i przetestowane 2026-09-07
na spogle.pl i krakowrolety.pl — raporty w `../audyt/senuto-skille/`.

| # | Skill | Pytanie właściciela | Co dostajesz | Wymaga | Koszt |
|---|---|---|---|---|---|
| 1 | [`gdzie-stoje/`](gdzie-stoje/SKILL.md) (v3) | „Jak stoję w Google i co nisko wisi?" | jedna kartka: skala, które strony pracują, 5–8 fraz z klientem tuż pod topem **wycenionych w zł**, kolumna AI, mapa, kanibalizacja, JEDNA rzecz na tydzień | Senuto MCP | 6–9 zapytań |
| 2 | [`luka-konkurencji/`](luka-konkurencji/SKILL.md) | „Kto mnie wyprzedza i NA CZYM?" | 3–7 **stron** (nie fraz) do zbudowania/wzmocnienia z priorytetem P1–P3, po odsiewie cudzych marek, innych miast, innych produktów | Senuto MCP (+Chrome gdy lista konkurentów pusta) | 5–8 zapytań |
| 3 | [`dlaczego-daleko/`](dlaczego-daleko/SKILL.md) | „Na frazę X jestem 25. — dlaczego?" | jedno zdanie werdyktu z numerem szczebla (zły typ strony → mapa/AIO/PAA → struktura vs mediana top10 → brakujące podtematy) + lista braków | Senuto + Chrome MCP + `crawl4ai` | 1–2 zapytania, 0 tokenów |
| 4 | [`co-sie-stalo/`](co-sie-stalo/SKILL.md) | „Spadło mi — co się stało i co robić?" | dla każdego spadku z klientem: przyczyna A (sam się przesunąłeś) / B (SERP się zmienił) / C (ktoś wyprzedził) / D (artefakt) + „czego NIE robić" | Senuto MCP (+Chrome) | 3–5 zapytań |
| 5 | [`jedna-strona-czy-dwie/`](jedna-strona-czy-dwie/SKILL.md) | „Te frazy to jedna strona czy kilka? Scalić czy rozbić?" | klastry intencji po nakładaniu SERP-ów + klasyfikator intencji + fan-out; decyzja: JEDNA STRONA / ZŁE DOPASOWANIE / KANIBALIZACJA (scal vs rozdziel) / BRAK | **NodesHub API** + Senuto | ~6 tokenów NH/fraza |

**Kolejność naturalna:** 1 → (2 lub 4) → 5 (która strona na co) → 3 (dlaczego ta strona przegrywa) → `/blisko-topu` (pisze gotowy tekst).

## Wspólny moduł `_senuto-wspolne/`
- `README.md` — filtr biznesowy (osąd → `journey_stage` → CPC), wzór wyceny, pułapki.
- `senuto_extended.py` — czyta 100-kB odpowiedzi `get_positions_data extended`: intencja, CPC, AIO/PAA/mapa, historia pozycji, `--bofu`, `--drops`.
- `crawl_serp.py` — Crawl4AI (długość) + surowy HTML (struktura: H2/H3/listy/tabele/liczby/ceny/FAQ) dla usera i top10; mediana.
- `topic_gap.py` — brakujące podtematy vs top10 (TF-IDF na n-gramach znakowych, bez klucza API).
- `nodeshub_serp.py` — wsadowe SERP-y NodesHub (`/v1/search` num=20, `/v1/intent-classifier`, `/v1/query-fanout`).
- `google-serp-chrome.md` — ekstraktor SERP-u z Chrome MCP (organic + PAA + AIO + local pack) jako fallback bez NodesHub.
- `check.py` — samotest zależności po instalacji.
- `serp_cluster.py` — klastry intencji po nakładaniu SERP-ów (≥2 wspólne w top3 lub ≥3 wspólne podstrony; strony główne nie liczą się).

## Instalacja (wyciągnięte z pudełka)
```
./install.sh                      # → ~/.claude/skills/ (globalnie, działa w każdym repo)
./install.sh /sciezka/do/projektu/.claude/skills   # → tylko w jednym projekcie
```
`install.sh` kopiuje 6 skilli + `_senuto-wspolne`, instaluje `requirements.txt`, Playwright chromium i uruchamia
`_senuto-wspolne/check.py`, który wypisuje ✓/✗ dla każdej zależności. Bez install.sh: skopiuj foldery ręcznie i odpal `check.py`.

**Co musi być poza pakietem:**
| Zależność | Które skille | Bez tego |
|---|---|---|
| **Senuto MCP** podpięty w Claude Code (`/mcp`) | wszystkie | nic nie działa — to źródło danych |
| Python 3.10+ i `requirements.txt` | 3 (crawl, TF-IDF), 5 (requests) | 1, 2, 4 działają bez Pythona (parser `senuto_extended.py` jest opcjonalny — da się czytać `extended` ręcznie) |
| `NODESHUB_API_KEY` w `.env` projektu | 5 | skill 5 przechodzi na Chrome MCP (bez klasyfikatora, SERP zlokalizowany) |
| Chrome MCP (Claude in Chrome) | 3, 4, 5 jako fallback SERP | gdy jest NodesHub — niepotrzebny; bez obu: user wkleja top10 |
| OpenSEO MCP | tylko 1, opcjonalny krok 7 | pomijany bez komentarza |

**Jak skille zapisują duże odpowiedzi MCP:** `get_positions_data extended` ma ~100 kB — Claude Code sam zapisuje taki wynik
do pliku `tool-results/…txt` i podaje ścieżkę; SKILL.md każe go skopiować do `data/...` i przepuścić przez `senuto_extended.py`.

**Ścieżki:** SKILL.md wołają `~/.claude/skills/_senuto-wspolne/<skrypt>` (instalacja globalna). Przy instalacji
w projekcie `install.sh` wypisze komendę `sed`, która podmienia ścieżkę na `.claude/skills/_senuto-wspolne/`.
Katalogi wyjściowe (`data/…`, `audyt/…`) skrypty i skille tworzą same w bieżącym katalogu roboczym.

## Dwie wersje pakietu
- **`./`** (ten poziom) — wersja techniczna: skrypty Python, crawl4ai, NodesHub przez API. Dla Claude Code.
- **`cowork/`** — wersja dla osób mniej technicznych: te same 6 skilli **bez Pythona i instalacji**; działa w Claude Cowork i w Claude Code. Zobacz `cowork/README.md`.

## Claude Code vs Claude Cowork
| Skill | Claude Code | Claude Cowork | Dlaczego |
|---|---|---|---|
| `/gdzie-stoje`, `/luka-konkurencji`, `/co-sie-stalo`, `/blisko-topu` | ✓ | ✓ (z konektorem Senuto włączonym w Cowork) | czysty MCP + pisanie plików; Python opcjonalny (`senuto_extended.py` tylko ułatwia czytanie `extended`) |
| `/dlaczego-daleko` | ✓ | częściowo — szczeble 1–2 (SERP przez Claude in Chrome) tak; szczebel 3–4 (crawl4ai + Playwright) **nie sprawdzone** w VM Cowork | Cowork uruchamia skrypty w odizolowanej maszynie wirtualnej; Playwright/Chromium i wyjście do internetu z VM nie są gwarantowane |
| `/jedna-strona-czy-dwie` | ✓ | **nie sprawdzone** — wymaga HTTP do `api.nodeshub.io` z VM Cowork; fallback Chrome MCP działa, ale bez klasyfikatora intencji | jw. |

Różnice, które wpływają na skille: w Cowork **filesystem VM resetuje się między sesjami** (raporty zapisuj w folderze
projektu, nie w `/tmp`), nie ma `~/.claude/skills/` — skill dodaje się przez interfejs Cowork (folder ze `SKILL.md`),
a ścieżki `~/.claude/skills/_senuto-wspolne/…` trzeba zastąpić ścieżką do folderu skilla w projekcie. Film: pokazuj w Claude Code;
do Cowork rekomenduj skille 1, 2, 4 i blisko-topu jako „działają z pudełka", 3 i 5 jako „Claude Code".

## Reguły, których nie ma w dokumentacji Senuto/NodesHub (zmierzone)
- `journey_stage` Senuto myli się na frazach lokalnych/wynajmowych („dmuchańce warszawa" = tofu przy CPC 8,64 zł) → CPC ≥ 5 zł bije etykietę; klasyfikator NodesHub (po SERP-ie) jest lepszy.
- Baza 2.0 (`country_id: "200"`) do pomiaru; `get_keywords/get_questions/get_groups` tylko baza 1.0.
- `get_competitors` bywa pusty w niszach → dobór ręczny z dwóch SERP-ów.
- Moduł SERP Senuto (`serp_create`) → 402 Paywall mimo limitu 6000/dzień. SERP przez NodesHub albo Chrome.
- Chrome pokazuje SERP zlokalizowany pod przeglądarkę → pozycja z Senuto, skład z Chrome; do klastrowania tylko NodesHub.
- Crawl4AI `PruningContentFilter` wycina nagłówki (35 H2 → 1) → struktura z HTML, długość z pruningu.
- Strony główne lokalnych firm rankują na wszystko → klastruj po podstronach i top3, nie po domenach.
