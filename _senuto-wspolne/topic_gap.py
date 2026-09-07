#!/usr/bin/env python3
"""
topic_gap.py — „pobieżna analiza semantyczna": których PODTEMATÓW nie masz, a ma większość top10.

Wejście: katalog z crawl_serp.py (sections.json = sekcje H2/H3 + tekst, z surowego HTML — nie z pruningu,
bo pruning wycina nagłówki). Wektory: TF-IDF na n-gramach znakowych 3–5 (po polsku bez lematyzacji, bez API).
Klastry: aglomeracyjne po cosinusie. Podtemat „wspólny" = obecny u ≥ --min-share konkurentów.

Użycie:
  python3 topic_gap.py data/dlaczego-daleko/rolety-krakow --min-share 0.5
"""
import argparse, json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--min-share", type=float, default=0.5)
    ap.add_argument("--threshold", type=float, default=0.85, help="dystans cos. łączenia (wyżej = szersze tematy)")
    a = ap.parse_args(); d = Path(a.dir); data = json.load(open(d / "sections.json"))
    mine = data["mine"]; docs, owner = [], []
    for url, secs in data["sections"].items():
        for h, t in secs:
            docs.append(f"{h}. {h}. {t}"); owner.append(("ja" if url == mine else url, h))
    comps = sorted({o for o, _ in owner if o != "ja"}); n = len(comps)
    if len(docs) < 4 or n < 2: print(f"za mało sekcji ({len(docs)}) / stron ({n}) do analizy"); return
    X = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True).fit_transform(docs)
    cl = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average", distance_threshold=a.threshold).fit(X.toarray())
    clusters = {}
    for i, lab in enumerate(cl.labels_): clusters.setdefault(lab, []).append(i)
    rows = []
    for idx in clusters.values():
        who = {owner[i][0] for i in idx}; comp_who = who - {"ja"}
        rows.append({"share": len(comp_who) / n, "mine": "ja" in who, "n_pages": len(comp_who),
                     "headings": [owner[i][1][:60] for i in idx if owner[i][0] != "ja"][:4],
                     "my_headings": [owner[i][1][:60] for i in idx if owner[i][0] == "ja"][:2]})
    rows.sort(key=lambda r: -r["share"])
    common = [r for r in rows if r["share"] >= a.min_share]
    my_secs = sum(1 for o, _ in owner if o == "ja")
    print(f"{len(docs)} sekcji ({my_secs} Twoich) z {n} stron konkurencji · {len(clusters)} podtematów · wspólnych (≥{int(a.min_share*100)}% top10): {len(common)}\n")
    print("PODTEMATY, KTÓRE MA WIĘKSZOŚĆ TOP10:")
    for r in common:
        flag = "MASZ   " if r["mine"] else "BRAK ← "
        print(f"  {flag} {int(r['share']*100):>3}% ({r['n_pages']} stron)  np.: " + " | ".join(r["headings"][:3]) + (f"   [Ty: {r['my_headings'][0]}]" if r["mine"] else ""))
    missing = [r for r in common if not r["mine"]]
    print(f"\nLUKA: {len(missing)} z {len(common)} wspólnych podtematów nie ma pokrycia na Twojej stronie.")
    json.dump({"common": common, "missing": missing}, open(d / "topic_gap.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__": main()
