"""Génère site/index.html à partir de travail-vs-aides.html.

La page source est écrite pour claude.ai (sans <html>/<head>, appels externes bloqués).
La version du site ajoute le squelette HTML et active les calculs OpenFisca en direct
pour les foyers modifiés et les profils personnalisés.

Usage : python site/build_site.py
"""
import io
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = io.open(ROOT / "travail-vs-aides.html", encoding="utf-8").read()

flag = "const LIVE_OF = false;"
assert src.count(flag) == 1, "drapeau LIVE_OF introuvable"
body = src.replace(flag, "const LIVE_OF = true;")

head = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="canonical" href="https://salaire-ou-aides.fr/">
<meta name="description" content="Simulateur pédagogique : revenu disponible et reste à vivre sans emploi ou en travaillant, pour des foyers types et votre propre profil. Barèmes 2026, calculs OpenFisca.">
<style>:root{color-scheme:light dark}body{margin:0}img{max-width:100%}</style>
</head>
<body>
"""
out = head + body + "\n</body>\n</html>\n"
dest = ROOT / "site" / "index.html"
io.open(dest, "w", encoding="utf-8").write(out)
print("écrit :", dest, f"({len(out)//1024} Ko)")
