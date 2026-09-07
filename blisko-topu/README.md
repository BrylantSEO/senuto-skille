# `/blisko-topu` — instalacja

Skill do Claude Code. Odpowiada na pytanie **„jestem na 12. miejscu i co dalej?"** — z pozycji
w Senuto robi gotowy tekst do wklejenia na stronę.

## Czego potrzebujesz

1. **Claude Code** (`npm install -g @anthropic-ai/claude-code`)
2. **Senuto MCP** — w Claude Code: `/mcp` → dodaj serwer `https://mcp.senuto.com/mcp` i zaloguj
   się swoim kontem Senuto. Bez kluczy API.

Nic więcej. Skill nie ma skryptów ani zależności.

## Instalacja

```bash
mkdir -p ~/.claude/skills/blisko-topu
# wrzuć SKILL.md do ~/.claude/skills/blisko-topu/
```

Restart Claude Code. Sprawdź: `/blisko-topu`.

## Użycie

```
/blisko-topu twojadomena.pl
```

Albo po prostu: *„sprawdź, gdzie twojadomena.pl jest blisko top3 i co z tym zrobić"*.

Pierwsze pytanie, które usłyszysz: **na czym Twoja firma zarabia i kto jest klientem.** Odpowiedz
jednym zdaniem — bez tego skill nie odróżni ruchu, który kupuje, od ruchu, który tylko ogląda.

## Co dostajesz

- tabelę 5 fraz: ile klików i złotych dołoży awans, ile to roboty,
- listę fraz **odrzuconych** wraz z powodem (często ciekawsza od tej pierwszej),
- dla 3 najlepszych: plik `poprawki-<fraza>.md` z gotowym tytułem, opisem i **napisanymi**
  sekcjami do wklejenia.

## Ile zużywa limitów Senuto

2–4 zapytania z „Analizy widoczności" (limit zwykle 400/dzień) i 0–3 z „Analizy SERP"
(zwykle 6000/dzień). Skill sam sprawdza limity na starcie i przerywa, jeśli jest ich za mało.
