# Ce que rapporte vraiment le travail

Simulateur pédagogique qui compare, pour des foyers types et pour un profil personnalisé, le **revenu disponible** et le **reste à vivre** sans emploi (en vivant des aides) et en travaillant. Barèmes d'octobre 2026, calculs des aides et de l'impôt avec [OpenFisca France](https://openfisca.org/fr/).

**Site en ligne : [salaire-ou-aides.fr](https://salaire-ou-aides.fr)**

> Outil pédagogique, pas un calcul de droits. Pour connaître vos droits réels : [mesdroitssociaux.gouv.fr](https://www.mesdroitssociaux.gouv.fr).

## Démarche

Ce site a un seul but : apporter de la clarté au débat « travailler est-il plus intéressant que vivre des aides ? », dans un but de transparence et **sans orientation politique**. Il n'est lié à aucun parti, syndicat, association, administration ou entreprise, ne reçoit aucun financement et n'affiche aucune publicité. Il montre les limites dans les deux sens et ne juge personne.

## Ce que fait le simulateur

- Compare 10 foyers types (personne seule, parents isolés, familles, handicap, retraite, auto-entrepreneur, salariés au salaire médian…) et un profil personnalisé.
- Calcule le RSA, la prime d'activité, l'aide au logement, les prestations familiales, l'AAH, l'ASPA, le chèque énergie et l'impôt avec OpenFisca.
- Ajoute les postes que les simulateurs officiels ne comptent pas : frais de transport (au kilomètre), garde d'enfants, repas, santé (mutuelle, franchises, dépassements), réductions locales, aide alimentaire.
- Propose des options réalistes : non-recours aux aides, emploi précaire avec chômage indemnisé.
- Affiche le reste à vivre après loyer, dépenses courantes et alimentation.

## Organisation du dépôt

| Fichier | Rôle |
|---|---|
| `travail-vs-aides.html` | Page source (modèle, données OpenFisca précalculées, interface) |
| `site/build_site.py` | Génère `site/index.html` pour le web, avec OpenFisca en direct |
| `site/index.html` | Page publiée (générée, ne pas modifier à la main) |
| `site/README.md` | Publication et mise à jour des barèmes |
| `site/make_images.py` | Génère le logo, les icônes et l'image de partage (`og.png`) |
| `site/fonts/` | Polices hébergées sur le site (licence SIL Open Font License) |
| `site/404.html` | Page d'erreur |
| `openfisca/of_grid.py` | Recalcule les grilles OpenFisca des foyers types |
| `openfisca/of_data.json` | Résultats de la dernière exécution |

## Utilisation locale

```bash
python site/build_site.py
```

Puis ouvrir `site/index.html` dans un navigateur. Aucune dépendance : Python 3 suffit pour les scripts, et la page est un fichier HTML autonome.

## Mettre à jour les barèmes

```bash
python openfisca/of_grid.py
```

Puis réintégrer `of_data.json` dans la constante `OFDATA` de `travail-vs-aides.html` et régénérer le site. Le détail est dans [site/README.md](site/README.md).

## Contribuer

Les corrections de barèmes, de règles ou de textes sont bienvenues : ouvrez une *issue* ou une *pull request* en indiquant la source officielle (Légifrance, CAF, service-public.fr, DREES…).

## Licences

- **Code** : [MIT](LICENSE).
- **Textes, tableaux et graphiques** : [CC BY 4.0](LICENSE-CONTENU.txt), en citant « salaire-ou-aides.fr ».
- Les données publiques citées restent soumises aux conditions de leurs producteurs.
