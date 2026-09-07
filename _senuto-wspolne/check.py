#!/usr/bin/env python3
"""check.py — sprawdza, czy pakiet skilli Senuto ma wszystko, czego potrzebuje. Uruchom po instalacji."""
import importlib, os, shutil, subprocess, sys
from pathlib import Path
ok = True
def row(name, good, hint=""):
    global ok; ok &= good or name.startswith("(opc)")
    print(f"  {'✓' if good else '✗'} {name}" + (f" — {hint}" if (not good and hint) else ""))
print("Python:", sys.version.split()[0]); row("Python ≥ 3.10", sys.version_info >= (3, 10))
for mod, skill in [("requests", "jedna-strona-czy-dwie"), ("bs4", "dlaczego-daleko"), ("sklearn", "dlaczego-daleko"), ("numpy", "dlaczego-daleko"), ("crawl4ai", "dlaczego-daleko")]:
    try: importlib.import_module(mod); row(f"moduł {mod}", True)
    except Exception: row(f"moduł {mod}", False, f"pip install {mod} (potrzebny dla /{skill})")
pw = list(Path.home().glob("Library/Caches/ms-playwright/chromium-*")) + list(Path.home().glob(".cache/ms-playwright/chromium-*"))
row("(opc) Playwright chromium (crawl w /dlaczego-daleko)", bool(pw), "python3 -m playwright install chromium")
key = os.environ.get("NODESHUB_API_KEY")
if not key:
    for d in [Path.cwd(), *Path.cwd().parents]:
        f = d / ".env"
        if f.exists() and "NODESHUB_API_KEY=" in f.read_text(): key = "z .env"; break
row("(opc) NODESHUB_API_KEY (tylko /jedna-strona-czy-dwie)", bool(key), "wpisz NODESHUB_API_KEY=... do .env projektu; 100 tokenów na start na nodeshub.io")
here = Path(__file__).parent
for s in ["senuto_extended.py", "crawl_serp.py", "topic_gap.py", "nodeshub_serp.py", "serp_cluster.py", "google-serp-chrome.md"]:
    row(f"plik _senuto-wspolne/{s}", (here / s).exists())
for s in ["gdzie-stoje", "luka-konkurencji", "dlaczego-daleko", "co-sie-stalo", "jedna-strona-czy-dwie", "blisko-topu"]:
    row(f"skill {s}/SKILL.md", (here.parent / s / "SKILL.md").exists())
print("\nSenuto MCP i Chrome MCP sprawdzisz w Claude Code: /mcp (Senuto = wymagany dla wszystkich; Chrome = fallback SERP).")
print("WYNIK:", "OK — pakiet kompletny" if ok else "BRAKI — patrz ✗ wyżej")
