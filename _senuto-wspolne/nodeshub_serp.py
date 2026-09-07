#!/usr/bin/env python3
"""
nodeshub_serp.py — wsadowe SERP-y z NodesHub (api.nodeshub.io) do formatu serp/<slug>.json
używanego przez serp_cluster.py / crawl_serp.py. Bez Chrome, bez lokalizacji pod przeglądarkę usera.

Endpointy (docs: nodeshub.io/docs):
  GET /v1/search?keyword&gl&hl&device&num      1 token/fraza  → organic (pełne URL-e), PAA, related, local_pack, AIO+sources
  GET /v1/intent-classifier?keyword&gl&hl      5 tokenów      → informational/commercial/transactional/navigational + %
  GET /v1/query-fanout?keyword&hl&mode         7.5 (standard) → warianty fraz z typem (related/specification/comparative/question…)

Użycie:
  python3 nodeshub_serp.py --out data/jedna-strona/spogle.pl --mine spogle.pl --keywords "agencja eventowa" "dmuchańce warszawa"
  python3 nodeshub_serp.py --out ... --mine ... --file frazy.txt --intent          # + klasyfikator intencji (5 tok./fraza)
  python3 nodeshub_serp.py --out ... --expand "agencja eventowa" --mine ...        # fan-out → serp/_fanout-<slug>.json
Zachowuje pola searches/cpc z istniejących plików (np. wpisane z Senuto). Klucz: NODESHUB_API_KEY w .env (szuka w górę drzewa).
"""
import argparse, json, os, re, sys, time
from pathlib import Path
from urllib.parse import urlparse
import requests

API = "https://api.nodeshub.io/v1"

def load_key():
    if os.environ.get("NODESHUB_API_KEY"): return os.environ["NODESHUB_API_KEY"]
    for d in [Path.cwd(), *Path.cwd().parents]:
        f = d / ".env"
        if f.exists():
            for line in f.read_text().splitlines():
                if line.startswith("NODESHUB_API_KEY="): return line.split("=", 1)[1].strip().strip('"')
    sys.exit("brak NODESHUB_API_KEY (env lub .env w górę drzewa)")

def get(path, key, **params):
    for attempt in range(3):
        r = requests.get(f"{API}/{path}", headers={"Authorization": f"Bearer {key}"}, params=params, timeout=60)
        if r.status_code == 200: return r.json()
        if r.status_code == 429: time.sleep(2 ** (attempt + 1)); continue
        if r.status_code == 402: sys.exit(f"402 — brak tokenów NodesHub: {r.text[:200]}")
        print(f"  ! {path} {r.status_code}: {r.text[:160]}", file=sys.stderr); return None
    return None

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("ł", "l").replace("ą", "a").replace("ę", "e").replace("ś", "s").replace("ć", "c").replace("ż", "z").replace("ź", "z").replace("ó", "o").replace("ń", "n")).strip("-")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--mine", required=True)
    ap.add_argument("--keywords", nargs="*", default=[]); ap.add_argument("--file"); ap.add_argument("--expand")
    ap.add_argument("--intent", action="store_true"); ap.add_argument("--gl", default="pl"); ap.add_argument("--hl", default="pl")
    ap.add_argument("--num", type=int, default=20); ap.add_argument("--force", action="store_true")
    a = ap.parse_args(); key = load_key(); out = Path(a.out) / "serp"; out.mkdir(parents=True, exist_ok=True)
    kws = list(a.keywords)
    if a.file: kws += [l.strip() for l in open(a.file) if l.strip() and not l.startswith("#")]
    if a.expand:
        fo = get("query-fanout", key, keyword=a.expand, hl=a.hl, mode="standard", add_questions="true")
        if fo:
            json.dump(fo, open(out / f"_fanout-{slug(a.expand)}.json", "w"), ensure_ascii=False, indent=1)
            print(f"FAN-OUT '{a.expand}': {fo.get('total_generated')} wariantów")
            for v in fo.get("generated_variants", []): print(f"   {v.get('type'):<14} {v.get('confidence'):.2f}  {v.get('keyword')}")
    tokens = 0
    for kw in kws:
        f = out / f"{slug(kw)}.json"; old = json.load(open(f)) if f.exists() else {}
        if old.get("source", "").startswith("nodeshub") and not a.force: print(f"= {kw} (cache)"); continue
        d = get("search", key, keyword=kw, gl=a.gl, hl=a.hl, device="desktop", num=a.num)
        if not d or not d.get("data", {}).get("success"): print(f"! {kw}: brak wyniku"); continue
        tokens += 1; r = d["data"]["results"]; sn = r.get("snippets", {}) or {}
        org = [{"url": o["url"], "title": o.get("title", ""), "pos": o.get("pos")} for o in r.get("organic_results", [])]
        mine = [o for o in org if a.mine in (urlparse(o["url"]).hostname or "")]
        aio = sn.get("ai_overview") or {}
        rec = {"keyword": kw, "source": "nodeshub 2026", "date": (d["data"].get("timestamp") or "")[:10],
               "organic": org, "paa": [q.get("text") for q in (sn.get("people_also_ask") or {}).get("questions", [])],
               "related": (sn.get("related_searches") or {}).get("queries", []),
               "has_local_pack": bool(sn.get("local_pack")), "local_pack": [p.get("name") for lp in (sn.get("local_pack") or []) for p in lp.get("places", [])][:5],
               "aio": (aio.get("text") or None) if aio else None, "aio_sources": [s.get("url") for s in aio.get("sources", [])] if aio else [],
               "snippets_found": r.get("snippets_found", []),
               "searches": old.get("searches"), "cpc": old.get("cpc"),
               "my_url": (urlparse(mine[0]["url"]).hostname.replace("www.", "") + urlparse(mine[0]["url"]).path) if mine else old.get("my_url"),
               "my_pos": mine[0]["pos"] if mine else (old.get("my_pos") if not org else None)}
        if a.intent:
            ic = get("intent-classifier", key, keyword=kw, gl=a.gl, hl=a.hl); tokens += 5
            if ic: rec["intent"] = ic
        json.dump(rec, open(f, "w"), ensure_ascii=False, indent=1)
        me = f"Ty {rec['my_pos']}. {rec['my_url']}" if rec.get("my_pos") else "Ty: brak w top%d" % a.num
        feats = ",".join(x for x in ["mapa" if rec["has_local_pack"] else "", "AIO" if rec["aio"] else "", f"PAA{len(rec['paa'])}" if rec["paa"] else ""] if x)
        print(f"+ {kw:<40} top3: {', '.join(urlparse(o['url']).hostname.replace('www.','') + urlparse(o['url']).path[:22] for o in org[:3])}  | {me} | {feats}" + (f" | intent: {json.dumps(rec['intent'].get('intent') or rec['intent'], ensure_ascii=False)[:80]}" if a.intent and rec.get("intent") else ""))
    print(f"\nzużyte tokeny (szac.): {tokens}", file=sys.stderr)

if __name__ == "__main__": main()
