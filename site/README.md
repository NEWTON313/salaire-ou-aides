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

## Publier sur GitHub Pages (gratuit)

1. Créer un dépôt sur GitHub, par exemple `rapporte-travail`.
2. Y déposer le contenu du dossier `site/` (au minimum `index.html`).
3. Dans le dépôt : Settings → Pages → Source « Deploy from a branch », branche `main`, dossier `/ (root)`.
4. La page est en ligne quelques minutes plus tard à l'adresse `https://<votre-compte>.github.io/rapporte-travail/`.

L'API publique d'OpenFisca (`api.fr.openfisca.org`) accepte les appels depuis n'importe quel site : aucun serveur n'est nécessaire.

## Mettre à jour les barèmes

Les barèmes changent en janvier (impôt, ASPA), en avril (RSA, prestations familiales, AAH), lors des hausses du SMIC et à la rentrée (bourses).

1. Relancer `python openfisca/of_grid.py` (l'API utilise automatiquement les derniers barèmes).
2. Réintégrer `of_data.json` dans la constante `OFDATA` de `travail-vs-aides.html`.
3. Mettre à jour les montants écrits en clair (recensement des aides, textes) et la date des barèmes.
4. Relancer `python site/build_site.py` et republier.

## Avant la mise en ligne

- Mentions légales : éditeur anonyme (LCEN art. 6-III-2), contact et hébergeur renseignés le 10 octobre 2026.
- Licences : code sous MIT (`LICENSE`), textes et graphiques sous CC BY 4.0 (`LICENSE-CONTENU.txt`), ajoutées le 10 octobre 2026.
- Vérifier deux ou trois profils avec le simulateur de la CAF ou mesdroitssociaux.gouv.fr.
