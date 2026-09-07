#!/usr/bin/env bash
# Instaluje pakiet skilli Senuto do ~/.claude/skills/ (domyślnie) lub do <katalog>/.claude/skills/ (argument).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-$HOME/.claude/skills}"
mkdir -p "$DEST"
for s in gdzie-stoje luka-konkurencji dlaczego-daleko co-sie-stalo jedna-strona-czy-dwie blisko-topu _senuto-wspolne; do
  rm -rf "$DEST/$s"; cp -R "$HERE/$s" "$DEST/$s"
done
python3 -m pip install -q -r "$HERE/requirements.txt"
python3 -m playwright install chromium >/dev/null 2>&1 || echo "! playwright install chromium nie przeszedł — /dlaczego-daleko (crawl) nie zadziała, reszta tak"
echo "Zainstalowano do: $DEST"
[ "$DEST" != "$HOME/.claude/skills" ] && echo "UWAGA: ścieżki w SKILL.md wskazują ~/.claude/skills/_senuto-wspolne/ — przy instalacji w projekcie użyj: sed -i '' 's|~/.claude/skills/_senuto-wspolne|.claude/skills/_senuto-wspolne|g' $DEST/*/SKILL.md"
python3 "$DEST/_senuto-wspolne/check.py"
