"""Génère une page indexable par situation (site/foyers/<slug>/index.html) et le sitemap.

Les chiffres sont calculés par compute.js (même modèle et mêmes données OpenFisca que le simulateur)
et écrits en clair dans le HTML, pour être lus par les moteurs de recherche sans JavaScript.
Appelé automatiquement par build_site.py.
"""
import html
import io
import json
import pathlib
import subprocess
import sys
from datetime import date

SITE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))
from seo_data import PAGES  # noqa: E402

URL = "https://salaire-ou-aides.fr"
IDS = ["karim", "sandrine", "diallo", "gerard", "lucas", "yanis", "sophie", "monique", "camille", "bernard"]
H1 = {
    "karim": "RSA ou SMIC pour une personne seule : ce que rapporte vraiment le travail",
    "sandrine": "Mère seule avec 2 enfants : RSA ou travailler, que rapporte un emploi ?",
    "diallo": "Famille de 4 enfants : vivre des aides ou travailler au SMIC ?",
    "gerard": "Travailler en zone rurale avec une voiture : est-ce rentable ?",
    "lucas": "Moins de 25 ans sans RSA : que rapporte un emploi au SMIC ?",
    "yanis": "Auto-entrepreneur : RSA, prime d'activité et revenu réel",
    "sophie": "AAH : quel niveau de vie face à un salarié au SMIC ?",
    "monique": "Retraite : minimum vieillesse ou carrière au salaire médian ?",
    "camille": "Salaire médian : combien de plus qu'en vivant des aides ?",
    "bernard": "Couple avec deux salaires médians et 2 enfants : l'écart avec les aides",
}

def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"

def labels(d):
    if d["retraite"]: return "Sans carrière (minimum vieillesse)", "Après 43 ans au salaire médian"
    if d["handicap"]: return "Avec l'AAH (ne peut pas travailler)", "Personne valide au SMIC"
    if d["ae"]: return "Sans activité (RSA)", "Auto-entrepreneur, CA équivalent au SMIC"
    if d["id"] == "bernard": return "Aucun des deux ne travaille", "Deux salaires médians"
    if d["id"] == "camille": return "Sans emploi", "Au salaire médian (2 190 € net)"
    return "Sans emploi", "Salarié au SMIC temps plein"

def lines(d):
    b, f = d["base"], d["full"]
    rows = [("Salaire ou revenu d'activité net", b["net"], f["net"]), ("Retraite", b["pension"], f["pension"]),
            ("RSA", b["rsa"], f["rsa"]), ("Prime d'activité", b["pa"], f["pa"]), ("Aide au logement", b["apl"], f["apl"]),
            ("Prestations familiales", b["fam"], f["fam"]), ("AAH et majoration", b["aah"], f["aah"]),
            ("Minimum vieillesse (ASPA)", b["aspa"], f["aspa"]), ("Contrat d'engagement jeune", b["cej"], f["cej"]),
            ("Frais du travail (transport, repas, garde)", -b["frais"], -f["frais"]),
            ("Santé (mutuelle, franchises)", -b["sante"], -f["sante"]), ("Impôt sur le revenu", -b["ir"], -f["ir"])]
    return [r for r in rows if r[1] or r[2]]

def page(d, slug, others):
    l0, l1 = labels(d)
    h1 = H1[d["id"]]
    gain = d["gain"]
    perday0 = d["rav0"] / 30 / d["persons"]; perday1 = d["rav1"] / 30 / d["persons"]
    desc = (f"{l0} : {eur(d['base']['rd'])} par mois ; {l1.lower()} : {eur(d['full']['rd'])}, soit {'+' if gain>=0 else '−'}{eur(abs(gain))}. "
            f"Reste à vivre de {eur(d['rav0'])} à {eur(d['rav1'])}. Calcul détaillé 2026 (aides, impôt, frais) avec OpenFisca.")
    title = f"{h1} (2026)"
    mx = max(d["base"]["rd"], d["full"]["rd"], 1)
    w = lambda v: max(0, v) / mx * 100
    table = "\n".join(f"<tr><td>{html.escape(n)}</td><td>{eur(a)}</td><td>{eur(c)}</td></tr>" for n, a, c in lines(d))
    other_links = "\n".join(f'<li><a href="/foyers/{s}/">{html.escape(t)}</a></li>' for s, t in others)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": f"{URL}/foyers/{slug}/",
           "inLanguage": "fr-FR", "isPartOf": {"@type": "WebSite", "name": "salaire-ou-aides.fr", "url": URL + "/"},
           "dateModified": date.today().isoformat()},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Simulateur", "item": URL + "/"},
              {"@type": "ListItem", "position": 2, "name": h1, "item": f"{URL}/foyers/{slug}/"}]}]
    kept = f"{d['kept10']:.1f}".replace(".", ",")
    verdict = (f"Travailler rapporte <b>{eur(gain)} de plus par mois</b>. Sur 10 € de revenu d'activité, il reste environ <b>{kept} €</b> en plus, "
               f"le reste compensant les aides qui baissent et les frais du travail." if not (d["retraite"] or d["handicap"]) else
               f"L'écart entre les deux situations est de <b>{eur(gain)} par mois</b>.")
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{URL}/foyers/{slug}/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="salaire-ou-aides.fr">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{URL}/foyers/{slug}/">
<meta property="og:image" content="{URL}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/fonts/fonts.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{--paper:#f3f5f9;--surface:#fff;--ink:#161e36;--muted:#56617c;--line:#d8deea;--work:#2547a6;--aid:#c27510;--gain:#1d7650;--loss:#b03636;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root{{--paper:#0e1321;--surface:#161d30;--ink:#e6eaf4;--muted:#98a3bd;--line:#29324d;--work:#86a2ff;--aid:#eaa845;--gain:#5ccb9b;--loss:#ef8080;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Source Sans 3","Segoe UI",system-ui,sans-serif}}
.wrap{{max-width:860px;margin:0 auto;padding-inline:20px;padding-block:28px 60px}}
a{{color:var(--work)}}
.brand{{display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font:700 1.05rem "Archivo","Arial Narrow",sans-serif;font-stretch:90%}}
.crumbs{{font-size:.85rem;color:var(--muted);margin:14px 0 8px}}
h1{{font:800 clamp(1.8rem,4.6vw,2.6rem)/1.1 "Archivo","Arial Narrow",sans-serif;font-stretch:85%;margin:0 0 12px;text-wrap:balance}}
h2{{font:750 1.35rem/1.2 "Archivo","Arial Narrow",sans-serif;font-stretch:85%;margin:34px 0 10px}}
.lead{{color:var(--muted);max-width:68ch}}
.verdict{{margin:18px 0;padding:16px 18px;border-left:4px solid var(--work);background:var(--surface);border-radius:0 10px 10px 0}}
.gauges{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:10px}}
@media (max-width:600px){{.gauges{{grid-template-columns:1fr}}}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px}}
.lab{{font:500 .7rem "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.bar{{display:flex;align-items:center;gap:8px;margin-top:8px;font:500 .9rem "IBM Plex Mono",monospace;white-space:nowrap}}
.bar span{{display:block;height:14px;border-radius:3px}}
.leg{{font-size:.85rem;color:var(--muted);margin-top:4px}}
table{{width:100%;border-collapse:collapse;font-size:.95rem;background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
th,td{{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left}}
td:nth-child(n+2),th:nth-child(n+2){{text-align:right;font-family:"IBM Plex Mono",monospace;white-space:nowrap}}
tr.tot td{{font-weight:700}}
.scroll{{overflow-x:auto}}
.cta{{display:inline-block;margin:6px 8px 0 0;padding:10px 18px;border-radius:8px;background:var(--work);color:var(--surface);font-weight:700;text-decoration:none}}
.cta.ghost{{background:transparent;color:var(--work);border:1px solid var(--work)}}
ul.others{{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px}}
ul.others a{{display:inline-block;padding:6px 12px;border:1px solid var(--line);border-radius:99px;background:var(--surface);text-decoration:none;font-size:.9rem}}
.note{{font-size:.85rem;color:var(--muted);margin-top:28px}}
</style>
</head>
<body>
<div class="wrap">
<a class="brand" href="/"><svg viewBox="0 0 64 64" width="28" height="28" aria-hidden="true"><rect width="64" height="64" rx="14" fill="var(--surface)" stroke="var(--line)" stroke-width="2"/><rect x="15" y="30" width="13" height="20" rx="3" fill="var(--aid)"/><rect x="36" y="14" width="13" height="36" rx="3" fill="var(--work)"/></svg>salaire-ou-aides.fr</a>
<nav class="crumbs"><a href="/">Simulateur</a> › Simulation par situation</nav>
<h1>{html.escape(h1)}</h1>
<p class="lead">{html.escape(d['desc'])}</p>
<p class="verdict">{verdict}</p>

<h2>Revenu disponible et reste à vivre par mois</h2>
<div class="gauges">
  <div class="card"><div class="lab">Revenu disponible</div>
    <div class="bar"><span style="width:{w(d['base']['rd'])*.7:.1f}%;background:var(--aid)"></span>{eur(d['base']['rd'])}</div>
    <div class="bar"><span style="width:{w(d['full']['rd'])*.7:.1f}%;background:var(--work)"></span>{eur(d['full']['rd'])}</div>
    <p class="leg">Salaires et aides, moins impôt, santé et frais du travail.</p></div>
  <div class="card"><div class="lab">Reste à vivre</div>
    <div class="bar"><span style="width:{w(d['rav0'])*.7:.1f}%;background:var(--aid)"></span>{eur(d['rav0'])}</div>
    <div class="bar"><span style="width:{w(d['rav1'])*.7:.1f}%;background:var(--work)"></span>{eur(d['rav1'])}</div>
    <p class="leg">Après loyer ({eur(d['loyer'])}), dépenses courantes et alimentation : {f"{perday0:.1f}".replace(".", ",")} € puis {f"{perday1:.1f}".replace(".", ",")} € par jour et par personne.</p></div>
</div>
<p class="leg"><span style="color:var(--aid)">■</span> {html.escape(l0)} &nbsp; <span style="color:var(--work)">■</span> {html.escape(l1)}</p>

<h2>Le détail poste par poste</h2>
<div class="scroll"><table>
<thead><tr><th>Par mois</th><th>{html.escape(l0)}</th><th>{html.escape(l1)}</th></tr></thead>
<tbody>
{table}
<tr class="tot"><td>Revenu disponible</td><td>{eur(d['base']['rd'])}</td><td>{eur(d['full']['rd'])}</td></tr>
<tr class="tot"><td>Reste à vivre</td><td>{eur(d['rav0'])}</td><td>{eur(d['rav1'])}</td></tr>
</tbody></table></div>

<h2>Simuler votre propre situation</h2>
<p>Changez le salaire, le loyer, le transport ou la composition du foyer dans le simulateur : les aides et l'impôt sont recalculés avec OpenFisca.</p>
<a class="cta" href="/#mon-profil">Faire ma simulation</a><a class="cta ghost" href="/#foyer-{d['id']}">Ouvrir ce foyer dans le simulateur</a>

<h2>Autres situations</h2>
<ul class="others">
{other_links}
</ul>

<p class="note">Outil pédagogique, pas un calcul de droits : foyer fictif, barèmes d'octobre 2026, aides et impôt calculés avec OpenFisca, frais et dépenses courantes estimés (<a href="/#methode">méthode</a>). Site indépendant, sans orientation politique (<a href="/#demarche">la démarche</a>). Vos droits réels : <a href="https://www.mesdroitssociaux.gouv.fr">mesdroitssociaux.gouv.fr</a>.</p>
</div>
</body>
</html>
"""

def main():
    data = {d["id"]: d for d in json.loads(subprocess.run(["node", str(SITE / "compute.js")], capture_output=True, text=True, encoding="utf-8", check=True).stdout)}
    urls = [(URL + "/", "1.0")]
    for (slug, label), pid in zip(PAGES, IDS):
        others = [(s, t) for s, t in PAGES if s != slug]
        dest = SITE / "foyers" / slug
        dest.mkdir(parents=True, exist_ok=True)
        io.open(dest / "index.html", "w", encoding="utf-8").write(page(data[pid], slug, others))
        urls.append((f"{URL}/foyers/{slug}/", "0.8"))
    today = date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{p}</priority></url>" for u, p in urls]
    sm.append("</urlset>")
    io.open(SITE / "sitemap.xml", "w", encoding="utf-8").write("\n".join(sm) + "\n")
    print(f"{len(urls)-1} pages par situation + sitemap ({len(urls)} adresses)")

if __name__ == "__main__":
    main()
