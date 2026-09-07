#!/usr/bin/env python3
"""
crawl_serp.py — pobiera stronę usera + strony z top10 i liczy metryki struktury.

DWA ŹRÓDŁA, bo jedno kłamie:
  • długość treści  → Crawl4AI `fit_markdown` (PruningContentFilter usuwa menu/stopkę/cookies),
  • struktura       → surowy HTML po wycięciu nav/header/footer/aside/script/cookie-bannerów,
    bo pruning WYCINA NAGŁÓWKI (krakowrolety.pl: 35 H2 w HTML → 1 w fit_markdown). Zmierzone 2026-09-07.

Użycie:
  python3 crawl_serp.py serp.json --mine https://krakowrolety.pl/ --out data/dlaczego-daleko/rolety-krakow
serp.json = {"keyword": "...", "organic": [{"url":..., "title":...}, ...], "paa": [...], "aio": ...}
Wynik: <out>/pages/*.html + *.md, <out>/sections.json (do topic_gap.py), <out>/metrics.json, tabela na stdout.
"""
import argparse, asyncio, json, re, sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

STRIP_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "aside", "form", "iframe", "svg", "button"]
# Dopasowanie po CAŁYM tokenie klasy/id, nie po podciągu — "widget" jako podciąg wycinał cały Elementor
# (elementor-widget-*), "menu" wycinał sekcje z "menu" w nazwie. Zmierzone 2026-09-07.
STRIP_TOKENS = {"cookie", "cookies", "cookie-banner", "cookie-notice", "cookieconsent", "consent", "gdpr", "rodo",
                "breadcrumb", "breadcrumbs", "popup", "modal", "newsletter", "navbar", "main-menu", "mobile-menu", "sidebar"}
def _strip_attr(v):
    if not v: return False
    toks = [t for t in (v if isinstance(v, list) else [v]) if t]
    return any(t.lower() in STRIP_TOKENS or t.lower().startswith(("cookie", "cky-", "cmplz", "moove")) for t in toks)
NUM = re.compile(r"(?<![\w.,])\d{1,3}(?:[  ]\d{3})*(?:[.,]\d+)?(?![\w])")
PRICE = re.compile(r"\d[\d  .,]*\s?(?:zł|PLN)\b", re.I)

async def crawl(urls):
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
    from crawl4ai.content_filter_strategy import PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, page_timeout=45000,
        markdown_generator=DefaultMarkdownGenerator(content_filter=PruningContentFilter(threshold=0.45, threshold_type="dynamic", min_word_threshold=8)))
    res = {}
    async with AsyncWebCrawler(verbose=False) as c:
        for u in urls:
            try:
                r = await c.arun(url=u, config=cfg)
                md = (r.markdown.fit_markdown if r.success and r.markdown else "") or ""
                res[u] = {"ok": bool(r.success and (r.html or "").strip()), "md": md, "html": r.html or "", "status": getattr(r, "status_code", None)}
            except Exception as e:
                res[u] = {"ok": False, "md": "", "html": "", "status": str(e)[:80]}
    return res

def main_soup(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(STRIP_TAGS): t.decompose()
    for t in soup.find_all(class_=_strip_attr): t.decompose()
    for t in soup.find_all(id=_strip_attr): t.decompose()
    return soup.find("main") or soup.find("article") or soup.body or soup

def sections(soup):
    """[(nagłówek, tekst pod nim)] — H2/H3 + wszystko do następnego nagłówka."""
    out = []
    for h in soup.find_all(["h2", "h3"]):
        title = h.get_text(" ", strip=True)
        buf = []
        for sib in h.find_all_next():
            if sib.name in ("h1", "h2", "h3"): break
            if sib.name in ("p", "li", "td", "th", "dd", "dt"): buf.append(sib.get_text(" ", strip=True))
        text = " ".join(buf)
        if title and len(text.split()) >= 10: out.append((title, text[:1500]))
    return out

def metrics(md, html):
    s = main_soup(html); text = s.get_text(" ", strip=True)
    words = len((md or text).split())
    heads = [h.get_text(" ", strip=True) for h in s.find_all(["h2", "h3"])]
    nums = set(n.strip() for n in NUM.findall(text) if n.strip() not in ("0",))
    return {"words": words, "words_html": len(text.split()), "h2": len(s.find_all("h2")), "h3": len(s.find_all("h3")),
            "bullets": len(s.find_all("li")), "table_rows": len(s.find_all("tr")), "unique_numbers": len(nums),
            "prices": len(PRICE.findall(text)), "faq_headings": sum(1 for h in heads if h.rstrip().endswith("?")),
            "images": len(s.find_all("img")), "headings": heads[:40]}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("serp"); ap.add_argument("--mine", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--top", type=int, default=10); ap.add_argument("--from-cache", action="store_true", help="przelicz metryki z zapisanych pages/*.html bez crawla")
    a = ap.parse_args()
    serp = json.load(open(a.serp)); out = Path(a.out); (out / "pages").mkdir(parents=True, exist_ok=True)
    mine_host = urlparse(a.mine).hostname.replace("www.", "")
    comp = [o["url"] for o in serp["organic"][:a.top] if urlparse(o["url"]).hostname.replace("www.", "") != mine_host]
    urls = [a.mine] + comp
    cached = {}
    if a.from_cache:
        for u in urls:
            slug = re.sub(r"[^a-z0-9]+", "-", u.lower())[:80].strip("-"); hp = out / "pages" / f"{slug}.html"
            if hp.exists():
                cached[u] = {"ok": bool(hp.read_text().strip()), "md": (out / "pages" / f"{slug}.md").read_text() if (out / "pages" / f"{slug}.md").exists() else "", "html": hp.read_text(), "status": "cache"}
    res = asyncio.run(crawl([u for u in urls if u not in cached])) if len(cached) < len(urls) else {}
    res.update(cached)
    table, secs = [], {}
    for i, u in enumerate(urls):
        r = res[u]; slug = re.sub(r"[^a-z0-9]+", "-", u.lower())[:80].strip("-")
        (out / "pages" / f"{slug}.md").write_text(r["md"]); (out / "pages" / f"{slug}.html").write_text(r["html"])
        m = metrics(r["md"], r["html"]) if r["ok"] else {}
        if r["ok"]: secs[u] = sections(main_soup(r["html"]))
        table.append({"url": u, "mine": u == a.mine, "rank": 0 if u == a.mine else i, "ok": r["ok"], "status": r["status"], **m})
    json.dump({"keyword": serp.get("keyword"), "paa": serp.get("paa"), "aio": serp.get("aio"), "pages": table}, open(out / "metrics.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"mine": a.mine, "sections": secs}, open(out / "sections.json", "w"), ensure_ascii=False)
    okc = [t for t in table if t["ok"] and not t["mine"]]
    def med(k):
        v = sorted(t[k] for t in okc); return v[len(v)//2] if v else 0
    print(f"{'#':>2} {'słowa':>6} {'H2':>3} {'H3':>3} {'listy':>5} {'tab':>4} {'liczby':>6} {'ceny':>4} {'FAQ':>3} {'img':>3}  url")
    for t in table:
        if not t["ok"]: print(f"{'ja' if t['mine'] else t['rank']:>2}  BŁĄD {t['status']}  {t['url']}"); continue
        print(f"{'ja' if t['mine'] else t['rank']:>2} {t['words']:>6} {t['h2']:>3} {t['h3']:>3} {t['bullets']:>5} {t['table_rows']:>4} {t['unique_numbers']:>6} {t['prices']:>4} {t['faq_headings']:>3} {t['images']:>3}  {t['url'][:66]}")
    if okc:
        print(f"\nMEDIANA top{len(okc)}: słowa {med('words')} · H2 {med('h2')} · H3 {med('h3')} · listy {med('bullets')} · tabele {med('table_rows')} · liczby {med('unique_numbers')} · ceny {med('prices')} · FAQ {med('faq_headings')} · img {med('images')}")
    print(f"zapisano → {out}/metrics.json, sections.json", file=sys.stderr)

if __name__ == "__main__": main()
