# Ce que rapporte vraiment le travail

Simulateur pédagogique qui compare, pour des foyers types et pour un profil personnalisé, le revenu disponible et le reste à vivre sans emploi et en travaillant. Barèmes d'octobre 2026.

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `../travail-vs-aides.html` | Page source (version publiée sur claude.ai, calculs OpenFisca précalculés) |
| `build_site.py` | Génère `index.html` pour le web, avec OpenFisca en direct |
| `index.html` | Page prête à héberger (ne pas modifier à la main : régénérer) |
| `../openfisca/of_grid.py` | Recalcule les grilles OpenFisca des foyers types |
| `../openfisca/of_data.json` | Résultats de la dernière exécution |

## Régénérer la page du site

```bash
python site/build_site.py
```

## Publication (Vercel relié à GitHub)

Le projet Vercel `salaire-ou-aides` est relié au dépôt GitHub `NEWTON313/salaire-ou-aides`, avec `site` comme dossier racine. Chaque envoi sur la branche `main` met le site en ligne automatiquement sur https://salaire-ou-aides.fr.

1. Modifier `travail-vs-aides.html`.
2. Régénérer la page : `python site/build_site.py`.
3. Envoyer : `git add -A`, `git commit -m "…"`, `git push`.

Vercel publie la nouvelle version en une minute environ. Les envois sur une autre branche créent une version de prévisualisation.

## Mettre à jour les barèmes

Les barèmes changent en janvier (impôt, ASPA), en avril (RSA, prestations familiales, AAH), lors des hausses du SMIC et à la rentrée (bourses).

1. Relancer `python openfisca/of_grid.py` (l'API utilise automatiquement les derniers barèmes).
2. Réintégrer `of_data.json` dans la constante `OFDATA` de `travail-vs-aides.html`.
3. Mettre à jour les montants écrits en clair (recensement des aides, textes) et la date des barèmes.
4. Relancer `python site/build_site.py`, puis committer et pousser sur GitHub.

## Avant la mise en ligne

- Mentions légales : éditeur anonyme (LCEN art. 6-III-2), contact et hébergeur renseignés le 10 octobre 2026.
- Licences : code sous MIT (`LICENSE`), textes et graphiques sous CC BY 4.0 (`LICENSE-CONTENU.txt`), ajoutées le 10 octobre 2026.
- Vérifier deux ou trois profils avec le simulateur de la CAF ou mesdroitssociaux.gouv.fr.
