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
import page_content  # noqa: E402

URL = "https://salaire-ou-aides.fr"
IDS = ["karim", "sandrine", "diallo", "gerard", "lucas", "yanis", "sophie", "monique", "camille", "bernard"]
H1 = {
    "karim": "RSA ou SMIC en 2026 : combien gagne-t-on vraiment en travaillant ?",
    "sandrine": "Mère seule avec 2 enfants : RSA ou travailler ? Le calcul 2026",
    "diallo": "Famille de 4 enfants : allocations, RSA ou salaire ? Le calcul 2026",
    "gerard": "Travailler avec une voiture en zone rurale : est-ce rentable en 2026 ?",
    "lucas": "Moins de 25 ans sans RSA : CEJ, prime d'activité ou emploi en 2026 ?",
    "yanis": "Prime d'activité auto-entrepreneur 2026 : montant, RSA et revenu réel",
    "sophie": "AAH 2026 : montant, cumul avec un salaire et niveau de vie",
    "monique": "Minimum vieillesse (ASPA) 2026 ou retraite d'une carrière : l'écart réel",
    "camille": "Salaire médian 2026 : combien de plus qu'en vivant des aides ?",
    "bernard": "Couple, deux salaires médians et 2 enfants : l'écart avec les aides en 2026",
}

def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"

def labels(d):
    if d["retraite"]: return "Sans carrière (minimum vieillesse)", "Après 43 ans au salaire médian"
    if d["handicap"]: return "Avec l'AAH (ne peut pas travailler)", "Personne valide au SMIC"
    if d["ae"]: return "Sans activité (RSA)", "Auto-entrepreneur, CA équivalent au SMIC"
    if d["id"] == "bernard": return "Aucun des deux ne travaille", "Deux salaires médians"
    if d["id"] == "camille": return "Sans emploi", "Au salaire médian (2 280 € net)"
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

AE_FAQ = [
    ("Un auto-entrepreneur a-t-il droit à la prime d'activité ?",
     "Oui. La prime d'activité est ouverte aux micro-entrepreneurs comme aux salariés, sous condition de ressources du foyer. "
     "La CAF ne retient pas tout le chiffre d'affaires : elle applique d'abord l'abattement forfaitaire du régime micro "
     "(50 % pour les prestations de services commerciales ou artisanales, 71 % pour la vente, 34 % pour les activités libérales)."),
    ("Quel chiffre d'affaires déclarer à la CAF ?",
     "Le chiffre d'affaires encaissé chaque mois du trimestre écoulé, avant cotisations, dans la déclaration trimestrielle de ressources. "
     "L'abattement forfaitaire est appliqué ensuite pour calculer les revenus retenus. Les cotisations versées à l'Urssaf ne sont pas déduites en plus."),
    ("Peut-on toucher le RSA et la prime d'activité en auto-entrepreneur ?",
     "Oui, quand le chiffre d'affaires est faible. Dans l'exemple de cette page (personne seule, services, loyer de 510 €), "
     "avec 800 € de chiffre d'affaires par mois, le RSA versé est d'environ {rsa800} et la prime d'activité d'environ {pa800}."),
    ("Combien de prime d'activité pour 1 500 € de chiffre d'affaires par mois ?",
     "Environ {pa1500} par mois pour une personne seule en prestations de services, sans autre revenu. "
     "Comme seule la moitié du chiffre d'affaires compte, la prime reste versée jusqu'à un chiffre d'affaires élevé : encore {pa3000} pour 3 000 € par mois."),
]

def ae_block(d):
    """Contenu propre à l'auto-entrepreneur : barème selon le chiffre d'affaires, règles CAF et questions fréquentes."""
    g = {r["ca"]: r for r in d["grid"]}
    rows = "\n".join(f"<tr><td>{eur(r['ca'])}</td><td><b>{eur(r['pa'])}</b></td><td>{eur(r['rsa'])}</td><td>{eur(r['apl'])}</td><td>{eur(r['rd'])}</td></tr>" for r in d["grid"])
    vals = dict(rsa800=eur(g[800]["rsa"]), pa800=eur(g[800]["pa"]), pa1500=eur(g[1500]["pa"]), pa3000=eur(g[3000]["pa"]))
    faq = [(q, a.format(**vals)) for q, a in AE_FAQ]
    body = f"""
<h2>Prime d'activité et RSA selon le chiffre d'affaires</h2>
<p>Personne seule en prestations de services (livraison, petits travaux…), loyer de {eur(d['loyer'])} à Bordeaux, sans autre revenu. Montants mensuels 2026, calculés avec OpenFisca.</p>
<div class="scroll"><table class="grid">
<thead><tr><th>Chiffre d'affaires</th><th>Prime d'activité</th><th>RSA</th><th>Aide au loge&shy;ment</th><th>Revenu dispo&shy;nible</th></tr></thead>
<tbody>
{rows}
</tbody></table></div>
<p class="leg">Montants par mois. Revenu disponible : chiffre d'affaires moins 21,3 % de cotisations, plus les aides, moins les frais professionnels (vélo, téléphone, assurance, CFE), la santé et l'impôt. Sans activité, il est de {eur(d['base']['rd'])}.</p>

<h2>Comment la CAF calcule la prime d'activité d'un auto-entrepreneur</h2>
<ul>
<li><b>Le chiffre d'affaires moins un abattement forfaitaire</b> : 50 % pour les services, 71 % pour la vente, 34 % pour les activités libérales. Avec 1 500 € de chiffre d'affaires en services, la CAF retient 750 € de revenus.</li>
<li><b>Les cotisations ne sont pas déduites en plus</b> : avec 21,3 % de cotisations sur les services, il reste 78,7 % du chiffre d'affaires, alors que la CAF n'en retient que 50 %. À revenu réellement perçu égal, la prime est donc souvent plus élevée que pour un salarié.</li>
<li><b>Une déclaration tous les trois mois</b> : le chiffre d'affaires de chaque mois du trimestre écoulé sert à calculer la prime des trois mois suivants. Un trimestre creux augmente la prime suivante, un bon trimestre la réduit.</li>
<li><b>Le RSA utilise la même base</b> : à faible chiffre d'affaires, RSA et prime d'activité se cumulent ; dans cet exemple, le RSA s'arrête entre 1 000 € et 1 200 € de chiffre d'affaires par mois.</li>
</ul>

<h2>Questions fréquentes</h2>
""" + "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return body, ld

FRAC = {0.25: "¼ SMIC", 0.5: "½ SMIC", 0.75: "¾ SMIC", 1: "SMIC", 1.25: "1,25 SMIC", 1.5: "1,5 SMIC", 2: "2 SMIC"}

def rsa_block(d):
    """Contenu propre à la page RSA ou SMIC : barème selon le salaire, explication de l'écart et questions fréquentes."""
    g = {r["k"]: r for r in d["grid"]}
    b, f = d["base"], d["full"]
    kept = f"{d['kept10']:.1f}".replace(".", ",")
    sans = {"k": 0, "net": 0, "rsa": b["rsa"], "pa": b["pa"], "apl": b["apl"], "rd": b["rd"]}
    rows = "\n".join(f"<tr><td>{eur(r['net'])} <span class=\"sub\">{FRAC.get(r['k'], 'sans emploi')}</span></td><td>{eur(r['rsa'])}</td>"
                     f"<td>{eur(r['pa'])}</td><td>{eur(r['apl'])}</td><td><b>{eur(r['rd'])}</b></td></tr>" for r in [sans] + d["grid"])
    faq = [
        ("Combien touche-t-on au RSA en 2026 ?",
         "Pour une personne seule sans enfant, le montant forfaitaire du RSA est de 651,69 € par mois. Si elle reçoit une aide au logement, "
         f"la CAF retire un forfait logement de 78,20 € : il reste environ {eur(b['rsa'])} versés, auxquels s'ajoute l'aide au logement ({eur(b['apl'])} ici)."),
        ("Quelle est la différence entre le RSA et le SMIC ?",
         f"Pour une personne seule locataire (loyer de {eur(d['loyer'])}), le revenu disponible passe de {eur(b['rd'])} sans emploi à {eur(f['rd'])} au SMIC à temps plein, "
         f"soit {eur(d['gain'])} de plus par mois, une fois le transport et la mutuelle payés. L'écart est plus faible que la différence entre le SMIC net (1 478 €) et le RSA, "
         "car l'aide au logement baisse et la prime d'activité ne compense qu'une partie du RSA perdu."),
        ("Peut-on toucher le RSA en travaillant ?",
         f"Oui, avec un petit salaire. Avec un quart de SMIC ({eur(g[0.25]['net'])} net), le RSA versé tombe à environ {eur(g[0.25]['rsa'])}, "
         f"et une prime d'activité de {eur(g[0.25]['pa'])} s'ajoute. Le RSA s'arrête quand le salaire net dépasse le RSA dû ; la prime d'activité prend alors le relais."),
        ("Jusqu'à quel salaire touche-t-on la prime d'activité ?",
         f"Pour une personne seule, la prime d'activité baisse au-dessus du SMIC : environ {eur(g[1.25]['pa'])} à 1,25 SMIC, puis plus rien à 1,5 SMIC "
         f"({eur(g[1.5]['net'])} net par mois) dans cet exemple."),
    ]
    body = f"""
<h2>RSA, prime d'activité et aide au logement selon le salaire</h2>
<p>Personne seule sans enfant, locataire à {eur(d['loyer'])} par mois, transport en commun. Montants mensuels 2026, calculés avec OpenFisca.</p>
<div class="scroll"><table class="grid">
<thead><tr><th>Salaire net</th><th>RSA</th><th>Prime d'activité</th><th>Aide au loge&shy;ment</th><th>Revenu dispo&shy;nible</th></tr></thead>
<tbody>
{rows}
</tbody></table></div>
<p class="leg">Revenu disponible : salaire et aides, moins l'impôt, la mutuelle, les franchises médicales et le transport. Le SMIC 2026 est de 1 867,02 € brut, soit 1 477,93 € net par mois à temps plein.</p>

<h2>Pourquoi l'écart entre RSA et SMIC est plus faible qu'on le croit</h2>
<ul>
<li><b>Le RSA disparaît</b> : {eur(b['rsa'])} par mois sans emploi, plus rien au SMIC.</li>
<li><b>L'aide au logement {"disparaît" if not f['apl'] else "baisse"}</b> : {eur(b['apl'])} sans emploi, {eur(f['apl'])} au SMIC.</li>
<li><b>La prime d'activité compense une partie</b> : {eur(f['pa'])} par mois au SMIC.</li>
<li><b>Travailler coûte</b> : transport ({eur(f['frais'])}) et santé ({eur(f['sante'])}), alors que la complémentaire santé solidaire est gratuite au RSA.</li>
</ul>
<p>Résultat : sur 10 € de salaire, il reste environ <b>{kept} €</b> de plus à la fin du mois. Travailler rapporte toujours davantage, mais beaucoup moins que l'écart affiché entre le SMIC et le RSA.</p>

<h2>Questions fréquentes</h2>
""" + "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return body, ld

def page(d, slug, others):
    l0, l1 = labels(d)
    h1 = H1[d["id"]]
    gain = d["gain"]
    perday0 = d["rav0"] / 30 / d["persons"]; perday1 = d["rav1"] / 30 / d["persons"]
    desc = (f"{l0} : {eur(d['base']['rd'])} par mois ; {l1} : {eur(d['full']['rd'])}, soit {'+' if gain>=0 else '−'}{eur(abs(gain))}. "
            f"Reste à vivre de {eur(d['rav0'])} à {eur(d['rav1'])}. Calcul détaillé 2026 (aides, impôt, frais) avec OpenFisca.")
    title = h1 if "2026" in h1 else f"{h1} (2026)"
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
    extra, extra_ld = ae_block(d) if d["ae"] else rsa_block(d) if d["id"] == "karim" else page_content.block(d)
    if extra_ld: ld.append(extra_ld)
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
h3{{font:700 1.05rem/1.3 "Archivo","Arial Narrow",sans-serif;margin:20px 0 4px}}
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
table.grid{{font-size:.88rem}} .sub{{font-size:.75em;color:var(--muted)}} table.grid th{{white-space:normal;vertical-align:bottom}} table.grid th,table.grid td{{padding:7px 8px}}
@media (max-width:600px){{table.grid .sub{{display:block}} table.grid{{font-size:.76rem}} table.grid th,table.grid td{{padding:6px 4px}}}}
.cta{{display:inline-block;margin:6px 8px 0 0;padding:10px 18px;border-radius:8px;background:var(--work);color:var(--surface);font-weight:700;text-decoration:none}}
.cta.ghost{{background:transparent;color:var(--work);border:1px solid var(--work)}}
ul.others{{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px}}
ul.others a{{display:inline-block;padding:6px 12px;border:1px solid var(--line);border-radius:99px;background:var(--surface);text-decoration:none;font-size:.9rem}}
.note{{font-size:.85rem;color:var(--muted);margin-top:28px}}
</style>
<script defer src="/_vercel/insights/script.js"></script>
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

{extra}
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
