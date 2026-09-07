#!/usr/bin/env python3
"""
serp_cluster.py — „jedna strona czy dwie?": klastruje frazy po NAKŁADANIU SIĘ SERP-ów, nie po słowach.

Wejście: katalog z plikami serp/<slug>.json, każdy:
  {"keyword": "...", "organic": [{"url": "...", "title": "..."}], "paa": [...], "aio": ..., "has_local_pack": bool,
   "searches": 720, "cpc": 8.64, "my_url": "spogle.pl/..." | null, "my_pos": 20 | null}
Reguła: dwie frazy = ta sama intencja, gdy dzielą ≥ --min-shared URL-i (domyślnie 3) w top10 ALBO ≥ 4 domeny.
Klastry: aglomeracyjnie (łączymy, gdy średnie nakładanie ≥ próg). Typ SERP-u: klasyfikacja URL-i
(oferta / miejska / cennik / blog / marketplace / social / wiki / katalog) → „intencja" = dominujący typ.
Wyjście: tabela klastrów + decyzja per klaster + clusters.json.

Użycie:
  python3 serp_cluster.py data/jedna-strona/spogle.pl --mine spogle.pl [--min-shared 3]
"""
import argparse, json, re, sys
from pathlib import Path
from urllib.parse import urlparse

def host(u): return (urlparse(u).hostname or "").replace("www.", "")
def path(u): return urlparse(u).path.rstrip("/") or "/"

SOCIAL = ("facebook.com", "instagram.com", "youtube.com", "tiktok.com", "linkedin.com", "pinterest.")
MARKET = ("olx.pl", "allegro.pl", "oferteo.pl", "fixly.pl", "panoramafirm.pl", "pkt.pl", "aleo.com", "gowork.pl", "mapa.targeo", "yelp", "ceneo.pl", "zumi.pl", "firmy.net", "cylex")
WIKI = ("wikipedia.org", "sjp.pl", "wsjp.pl")
CITIES = ("warszaw", "krak", "poznan", "wroclaw", "gdansk", "lodz", "katowic", "lublin", "szczecin", "bydgoszcz", "bialystok", "rzeszow", "torun", "kielc", "olsztyn", "opole", "gliwic", "radom", "sosnowiec")

def page_type(u):
    h, p = host(u), path(u).lower()
    if any(s in h for s in SOCIAL): return "social"
    if any(m in h for m in MARKET): return "marketplace/katalog"
    if any(w in h for w in WIKI): return "wiki"
    if p == "/": return "oferta (strona główna)"
    if re.search(r"cennik|cena|koszt|ile-kosztuje", p): return "cennik"
    if re.search(r"/blog|/poradnik|/artykul|/aktualnosci|/news|/porady|/\d{4}/", p): return "blog"
    if re.search(r"ranking|najlepsz|top-\d|-vs-|porownanie", p): return "ranking/porównanie"
    if any(c in p for c in CITIES): return "strona miejska"
    return "oferta (podstrona)"

def key(o): return path(o["url"]) + "@" + host(o["url"])
def overlap(a, b):
    """(wspólne URL-e top10, wspólne domeny top10, wspólne URL-e top3, wspólne NIE-strony-główne top10).
    Strony główne lokalnych firm rankują na wszystko — liczą się mniej niż dedykowane podstrony."""
    ua = {key(o) for o in a["organic"][:10]}; ub = {key(o) for o in b["organic"][:10]}
    da = {host(o["url"]) for o in a["organic"][:10]}; db = {host(o["url"]) for o in b["organic"][:10]}
    t3 = {key(o) for o in a["organic"][:3]} & {key(o) for o in b["organic"][:3]}
    nonhome = {k for k in ua & ub if not k.startswith("/@")}
    return len(ua & ub), len(da & db), len(t3), len(nonhome)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--mine", required=True, help="domena usera")
    ap.add_argument("--min-shared", type=int, default=3, help="wspólne URL-e w top10 = ta sama intencja")
    ap.add_argument("--min-domains", type=int, default=4, help="albo wspólne domeny")
    a = ap.parse_args(); d = Path(a.dir)
    serps = [json.load(open(f)) for f in sorted((d / "serp").glob("*.json")) if not f.name.startswith("_")]
    if len(serps) < 2: print("potrzeba ≥ 2 plików serp/*.json"); return
    n = len(serps)
    same = [[False] * n for _ in range(n)]; ov = [[(0, 0)] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            u, dm, t3, nh = overlap(serps[i], serps[j]); ov[i][j] = ov[j][i] = (u, dm)
            # TA SAMA STRONA gdy: ≥2 wspólne wyniki w TOP3 albo ≥3 wspólne dedykowane podstrony w top10.
            # Same domeny / same strony główne to za mało — w lokalnych SERP-ach te same firmy rankują stroną główną
            # na „rolety kraków" i podstronami na „rolety zewnętrzne kraków" (zmierzone 2026-09-07: to osobne intencje).
            same[i][j] = same[j][i] = (t3 >= 2 or nh >= a.min_shared)
    # klastry = spójne składowe grafu „ta sama intencja" (z wymogiem, by nowa fraza pasowała do ≥ połowy klastra)
    clusters, assigned = [], [False] * n
    order = sorted(range(n), key=lambda i: -(serps[i].get("searches") or 0))
    for i in order:
        if assigned[i]: continue
        cl = [i]; assigned[i] = True
        for j in order:
            if assigned[j]: continue
            if sum(same[j][k] for k in cl) >= max(1, (len(cl) + 1) // 2): cl.append(j); assigned[j] = True
        clusters.append(cl)
    out = []
    print(f"{n} fraz → {len(clusters)} klastrów intencji (próg: ≥2 wspólne wyniki w top3 lub ≥{a.min_shared} wspólne podstrony w top10)\n")
    for ci, cl in enumerate(clusters, 1):
        types = {}
        for i in cl:
            for o in serps[i]["organic"][:10]: t = page_type(o["url"]); types[t] = types.get(t, 0) + 1
        tot = sum(types.values()) or 1
        dom = sorted(types.items(), key=lambda x: -x[1])
        intent = " / ".join(f"{t} {int(100*c/tot)}%" for t, c in dom[:3])
        my_urls = {serps[i].get("my_url") for i in cl if serps[i].get("my_url")}
        vol = sum(serps[i].get("searches") or 0 for i in cl)
        feats = set()
        for i in cl:
            if serps[i].get("aio"): feats.add("AIO")
            if serps[i].get("has_local_pack"): feats.add("mapa")
        # decyzja
        if len(my_urls) > 1: decision = f"KANIBALIZACJA — {len(my_urls)} Twoje strony na jednej intencji → scal (301 słabszej) albo rozdziel intencje"
        elif len(my_urls) == 1:
            mu = next(iter(my_urls)); mt = page_type("https://" + mu if not mu.startswith("http") else mu)
            lead = dom[0][0]
            mismatch = lead.split(" (")[0] != mt.split(" (")[0] and not (lead.startswith("oferta") and mt.startswith("oferta"))
            decision = f"JEDNA STRONA — masz: {mu}" + (f"; ale SERP chce '{lead}', a Ty dajesz '{mt}' → ZŁE DOPASOWANIE, potrzebna inna strona" if mismatch else "")
        else: decision = "BRAK STRONY — jedna nowa strona na cały klaster (jeśli ma klienta)"
        print(f"## Klaster {ci} · {vol} szukań/mies. · intencja: {intent}" + (f" · {', '.join(sorted(feats))}" if feats else ""))
        for i in cl:
            s = serps[i]; me = f"Ty: {s.get('my_pos')}. {s.get('my_url')}" if s.get("my_pos") else (f"Ty: >20 {s.get('my_url')}" if s.get("my_url") else "Ty: brak")
            ic = (s.get("intent") or {}).get("classifications") or {}
            if ic: me += "  [" + "/".join(str((ic.get(k) or {}).get("value", "?")).lower() for k in ("main_intent", "journey_stage", "content_timeliness")) + "]"
            top3 = ", ".join(host(o["url"]) + path(o["url"])[:25] for o in s["organic"][:3])
            print(f"   • {s['keyword']:<38} {s.get('searches') or '?':>5}  {me:<70} top3: {top3}")
        print(f"   → {decision}\n")
        out.append({"cluster": ci, "keywords": [serps[i]["keyword"] for i in cl], "searches": vol, "intent": dom, "my_urls": sorted(my_urls), "decision": decision})
    # RYNEK: te same domeny (≥ min_domains) = ta sama grupa firm walczy o obie frazy, nawet jeśli osobnymi stronami
    print("TEN SAM RYNEK, OSOBNE STRONY (≥%d wspólnych domen, <%d wspólnych URL-i) — u siebie też rób osobne podstrony:" % (a.min_domains, a.min_shared))
    for i in range(n):
        for j in range(i + 1, n):
            u, dm = ov[i][j]
            if not same[i][j] and dm >= a.min_domains:
                print(f"   {serps[i]['keyword']}  ≠  {serps[j]['keyword']}  ({u} URL, {dm} domen)")
    print()
    # pary „blisko, ale osobno" — do ręcznego osądu
    print("PARY NA GRANICY (2 wspólne URL-e / 3 domeny — osąd ręczny):")
    for i in range(n):
        for j in range(i + 1, n):
            u, dm = ov[i][j]
            if not same[i][j] and dm < a.min_domains and (u == a.min_shared - 1 or dm == a.min_domains - 1):
                print(f"   {serps[i]['keyword']}  ~  {serps[j]['keyword']}  ({u} URL, {dm} domen)")
    json.dump(out, open(d / "clusters.json", "w"), ensure_ascii=False, indent=1)
    print(f"\nzapisano → {d}/clusters.json", file=sys.stderr)

if __name__ == "__main__": main()
