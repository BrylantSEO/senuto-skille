#!/usr/bin/env python3
"""
senuto_extended.py — wspólny parser odpowiedzi `get_positions_data` z detail_level: extended.

Zamienia 100 kB JSON-a na tabelę, którą da się przeczytać: fraza · pozycja · intencja
(journey_stage) · CPC · wolumen · AIO/PAA · historia · wins/losses · URL.
Filtr biznesowy = `--bofu` (zostawia bofu+mofu). `--drops` = frazy, które straciły ≥3 pozycje
między pierwszym a ostatnim punktem historii. `--gains` analogicznie.

Użycie:
  python3 senuto_extended.py positions_extended.json                 # cała tabela
  python3 senuto_extended.py positions_extended.json --bofu          # tylko kupujące
  python3 senuto_extended.py positions_extended.json --drops --min-searches 50
  python3 senuto_extended.py positions_extended.json --json out.json # do dalszych skryptów
"""
import argparse, json, sys

def g(d, *p, default=None):
    for k in p:
        if not isinstance(d, dict) or k not in d: return default
        d = d[k]
    return d if d is not None else default

def rows(data):
    out = []
    for k in data.get("keywords", []):
        st = k.get("statistics", {})
        hist = g(st, "position", "history", default={}) or {}
        dates = sorted(hist)
        first = hist[dates[0]]["position"] if dates else None
        last = hist[dates[-1]]["position"] if dates else None
        snip = g(st, "snippets", "current", default=[]) or []
        trends = g(st, "trends", "history", default=[]) or []
        out.append({
            "keyword": k.get("keyword"),
            "position": g(st, "position", "current"),
            "prev": g(st, "position", "previous"),
            "diff": g(st, "position", "diff"),
            "wins": g(st, "position", "changes", "wins", default=0),
            "losses": g(st, "position", "changes", "losses", default=0),
            "hist_first": first, "hist_last": last, "hist_dates": dates,
            "searches": g(st, "searches", "current", default=0),
            "cpc": g(st, "cpc", "current", default=0),
            "kd": g(st, "difficulty", "current"),
            "visibility": g(st, "visibility", "current", default=0),
            "url": g(st, "url", "current", default=""),
            "url_prev": g(st, "url", "previous", default=""),
            "url_changed": g(st, "url", "is_change", default=0),
            "stage": g(st, "intentions", "journey_stage", default="?"),
            "intent": g(st, "intentions", "main_intent", default="?"),
            "action": g(st, "intentions", "action_type", default="?"),
            "timeliness": g(st, "intentions", "content_timeliness", default="?"),
            "aio": "ai_overview" in snip,
            "paa": "people_also_ask" in snip,
            "map": "map" in snip,
            "trend_min": min(trends) if trends else None,
            "trend_max": max(trends) if trends else None,
        })
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file"); ap.add_argument("--bofu", action="store_true")
    ap.add_argument("--drops", action="store_true"); ap.add_argument("--gains", action="store_true")
    ap.add_argument("--min-searches", type=int, default=0); ap.add_argument("--json")
    a = ap.parse_args()
    data = json.load(open(a.file))
    r = rows(data)
    if a.bofu: r = [x for x in r if x["stage"] in ("bofu", "mofu")]
    if a.min_searches: r = [x for x in r if x["searches"] >= a.min_searches]
    if a.drops: r = [x for x in r if x["hist_first"] and x["hist_last"] and x["hist_last"] - x["hist_first"] >= 3]
    if a.gains: r = [x for x in r if x["hist_first"] and x["hist_last"] and x["hist_first"] - x["hist_last"] >= 3]
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1); print(f"zapisano {len(r)} → {a.json}")
    print(f"{'fraza':42} {'poz':>3} {'hist':>7} {'w/l':>5} {'stage':5} {'szuk':>5} {'cpc':>6} {'kd':>3} AIO PAA  url")
    for x in r:
        h = f"{x['hist_first']}→{x['hist_last']}" if x["hist_first"] else "-"
        print(f"{x['keyword'][:42]:42} {x['position']:>3} {h:>7} {x['wins']}/{x['losses']:<3} {x['stage']:5} {x['searches']:>5} {x['cpc']:>6.2f} {x['kd'] or 0:>3} {'✓' if x['aio'] else '·'}   {'✓' if x['paa'] else '·'}   {x['url'][:60]}")
    print(f"\n{len(r)} fraz | daty historii: {r[0]['hist_dates'] if r and r[0]['hist_dates'] else '-'}", file=sys.stderr)

if __name__ == "__main__": main()
