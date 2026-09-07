# Skille Senuto — wersja dla osób mniej technicznych (Claude Cowork / Claude Code bez terminala)

Te same 5 skilli + `/blisko-topu`, ale **bez Pythona, bez instalacji, bez skryptów**. Wszystko, co w wersji technicznej robiły
skrypty, tu robi Senuto MCP, Claude in Chrome (skrypt uruchamiany w przeglądarce) albo NodesHub MCP.

| Skill | Pytanie | Potrzebuje |
|---|---|---|
| `gdzie-stoje` | Jak stoję i co nisko wisi (w zł)? | Senuto MCP |
| `luka-konkurencji` | Kto mnie wyprzedza i na czym? | Senuto MCP (+Chrome, gdy lista konkurentów pusta) |
| `co-sie-stalo` | Spadło mi — która z 3 przyczyn? | Senuto MCP (+Chrome) |
| `dlaczego-daleko` | Na frazę X jestem 25. — dlaczego? | Senuto MCP + Claude in Chrome |
| `jedna-strona-czy-dwie` | Te frazy to jedna strona czy kilka? | Senuto MCP + NodesHub MCP **lub** Chrome |
| `blisko-topu` | Gotowy tekst do wklejenia dla 3 fraz | Senuto MCP |

Kolejność: gdzie-stoje → (luka / co-sie-stalo) → jedna-strona-czy-dwie → dlaczego-daleko → blisko-topu.

## Instalacja
**Claude Cowork:** dodaj każdy folder (np. `gdzie-stoje/`) jako skill w ustawieniach Cowork → Skills (folder ze `SKILL.md`). Włącz
konektor **Senuto** (claude.ai → Connectors). Raporty zapisuj w folderze projektu — system plików Cowork resetuje się między sesjami.
**Claude Code:** skopiuj foldery do `~/.claude/skills/`. Bez `install.sh`, bez `pip`.

**NodesHub jako MCP (opcjonalnie, tylko `jedna-strona-czy-dwie`):** klucz z nodeshub.io (100 tokenów bez rejestracji), w konfiguracji
Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{ "mcpServers": { "nodeshub": { "command": "npx", "args": ["-y", "serpdata-mcp"], "env": { "SERPDATA_API_KEY": "twój-klucz" } } } }
```
Bez NodesHub skill używa Claude in Chrome (wyniki zlokalizowane pod Twoją przeglądarkę, bez klasyfikatora intencji).

## Czym różni się od wersji technicznej (`../`)
- `get_positions_data extended` z `limit: 25` zamiast 50 — odpowiedź trafia do rozmowy, nie do pliku; parser niepotrzebny.
- Pomiar struktury stron (`dlaczego-daleko`) skryptem JS w przeglądarce zamiast crawl4ai — dokładniejszy (bez pruningu, który wycinał nagłówki).
- Brakujące podtematy: z listy nagłówków top10 osądem, zamiast TF-IDF.
- Klastrowanie SERP-ów (`jedna-strona-czy-dwie`) w głowie z tabelą par jako dowodem — działa do ~15 fraz; powyżej użyj wersji technicznej.
- Nie sprawdzone w Cowork: czy `serpdata-mcp` wstaje w Cowork tak jak w Claude Desktop. Chrome jako fallback działa wszędzie, gdzie jest Claude in Chrome.

## Reguły zmierzone przy budowie (obowiązują w obu wersjach)
- `journey_stage` Senuto myli się na frazach lokalnych/wynajmowych → CPC ≥ 5 zł bije etykietę; klasyfikator NodesHub (po wynikach) jest lepszy.
- Baza 2.0 (`country_id: "200"`) do pomiaru; `get_keywords/get_questions/get_groups` tylko `"1"`.
- `get_competitors` bywa pusty w niszach → dobór ręczny z dwóch wyszukań.
- Moduł SERP Senuto (`serp_create`) → 402 Paywall mimo limitu — wyniki przez NodesHub albo Chrome.
- Chrome pokazuje wyniki zlokalizowane → pozycja z Senuto, skład wyników z Chrome; do klastrowania lepiej NodesHub.
- Strony główne lokalnych firm rankują na wszystko → klastruj po podstronach i top3, nie po domenach.
