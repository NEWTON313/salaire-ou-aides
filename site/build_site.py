"""Génère site/index.html à partir de travail-vs-aides.html.

La page source est écrite pour claude.ai (sans <html>/<head>, appels externes bloqués).
La version du site ajoute le squelette HTML, les balises de partage et de référencement,
les polices hébergées localement, et active les calculs OpenFisca en direct
pour les foyers modifiés et les profils personnalisés.

Usage : python site/build_site.py
"""
import io
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://salaire-ou-aides.fr/"
TITLE = "Ce que rapporte vraiment le travail"
DESC = ("Vivre des aides ou travailler : le calcul foyer par foyer, une fois tout compté "
        "(aides, impôt, santé, transport, garde, loyer). Simulateur pédagogique, barèmes 2026, calculs OpenFisca.")

src = io.open(ROOT / "travail-vs-aides.html", encoding="utf-8").read()

flag = "const LIVE_OF = false;"
assert src.count(flag) == 1, "drapeau LIVE_OF introuvable"
body = src.replace(flag, "const LIVE_OF = true;")

# Polices : Google Fonts (page claude.ai) remplacé par les fichiers hébergés sur le site
google = [
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n',
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..125,500..800&family=Source+Sans+3:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">\n',
]
for g in google:
    assert body.count(g) == 1, "lien Google Fonts introuvable"
    body = body.replace(g, "")
# le <title> de la page source est remplacé par celui du <head>
body = body.replace(f"<title>{TITLE}</title>\n", "", 1)

ld = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": TITLE,
    "url": URL,
    "description": DESC,
    "applicationCategory": "FinanceApplication",
    "operatingSystem": "Tous navigateurs",
    "inLanguage": "fr-FR",
    "isAccessibleForFree": True,
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
    "license": "https://salaire-ou-aides.fr/LICENSE.txt",
}

head = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{URL}">
<meta name="theme-color" content="#0e1321" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f3f5f9" media="(prefers-color-scheme: light)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="salaire-ou-aides.fr">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{URL}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Ce que rapporte vraiment le travail : 3,4 € restent en plus sur 10 € de salaire au SMIC.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{URL}og.png">
<link rel="preload" href="/fonts/archivo-latin-b92029.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/source-sans-3-latin-263ee0.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts/fonts.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>:root{{color-scheme:light dark}}body{{margin:0}}img{{max-width:100%}}</style>
</head>
<body>
"""
out = head + body + "\n</body>\n</html>\n"
dest = ROOT / "site" / "index.html"
io.open(dest, "w", encoding="utf-8").write(out)
print("écrit :", dest, f"({len(out)//1024} Ko)")
