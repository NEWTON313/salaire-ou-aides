# Plan de diffusion : obtenir des liens vers salaire-ou-aides.fr

Objectif : que d'autres sites crédibles parlent du simulateur et y renvoient. Ce sont ces liens qui font le plus progresser le site dans Google.

Règles à garder en tête :
- **Toujours dire que vous êtes l'auteur** du site. C'est plus honnête, et le spam déguisé est sanctionné (bannissement Reddit, signalement Facebook).
- **Un message adapté par destinataire**, jamais le même copier-coller partout.
- **Mettre en avant l'utilité et la neutralité**, pas la promotion.

---

## Priorité 1 : liens les plus solides

### 1. data.gouv.fr : déclarer une « réutilisation »
data.gouv.fr permet de signaler un projet qui utilise des données ou outils publics. Le site utilise OpenFisca et les barèmes publics : c'est exactement le cadre. Un lien depuis un site public est très bien considéré par Google.

- Où : https://www.data.gouv.fr/fr/reuses/ → « Publier une réutilisation » (compte data.gouv.fr gratuit, à créer par vous).
- Type : « Application ». Thème : « Social ».
- Titre : Ce que rapporte vraiment le travail : simulateur aides ou salaire
- Description à coller :

> Simulateur pédagogique et neutre qui compare, foyer par foyer, le revenu disponible et le reste à vivre sans emploi (RSA, prime d'activité, aide au logement, prestations familiales, AAH, ASPA…) et en travaillant, une fois l'impôt, la santé, le transport, la garde et le loyer comptés. Les aides et l'impôt sont calculés avec OpenFisca France (barèmes d'octobre 2026). 10 situations types et une simulation personnalisée. Code source public (licence MIT), contenus sous licence CC BY 4.0.

- À lier aux jeux de données ou outils utilisés : OpenFisca, barèmes des prestations sociales (IPP), si proposés.

### 2. Communauté OpenFisca
L'équipe OpenFisca met en avant les projets qui utilisent son moteur.
- Où : le dépôt GitHub `openfisca/openfisca-france` (onglet Discussions s'il est ouvert) ou le contact indiqué sur https://openfisca.org/fr/.
- Message :

> Bonjour,
> J'ai créé salaire-ou-aides.fr, un simulateur pédagogique qui utilise l'API publique d'OpenFisca France pour comparer, foyer par foyer, le revenu disponible et le reste à vivre avec ou sans emploi (RSA, prime d'activité, APL, AAH, ASPA, impôt). OpenFisca m'a aussi permis de corriger plusieurs règles fines (neutralisation de la hausse de l'ASF dans le RSA, majorations pour âge, zonage APL).
> Le code est public (MIT) : https://github.com/NEWTON313/salaire-ou-aides
> Si le projet vous semble utile, je serais ravi qu'il figure parmi les réutilisations d'OpenFisca. Toute remarque sur la modélisation est aussi la bienvenue.

---

## Priorité 2 : communautés en ligne

### 3. Reddit r/vosfinances (finances personnelles)
- Où : https://www.reddit.com/r/vosfinances/ (vérifier d'abord les règles du sous-forum sur l'autopromotion).
- Titre : J'ai fait un simulateur pour comparer RSA et salaire, foyer par foyer, une fois tout compté (barèmes 2026)
- Texte :

> Bonjour,
> Je suis l'auteur de ce petit site, sans pub ni collecte de données : https://salaire-ou-aides.fr
> L'idée : sortir du débat « au RSA on gagne autant qu'en travaillant » avec des chiffres. Les aides et l'impôt sont calculés avec OpenFisca (le moteur public derrière mesdroitssociaux.gouv.fr), et j'ajoute ce que les simulateurs officiels ne comptent pas : transport au kilomètre, garde, mutuelle, loyer.
> Ce qui ressort : travailler rapporte toujours plus, mais au SMIC il ne reste en moyenne qu'environ 3,40 € sur 10 € gagnés, et parfois moins de 200 € par mois d'écart (parent seul, voiture obligatoire).
> Le code est public. Je cherche surtout des retours : erreurs de règles, situations à ajouter, points pas clairs.

### 4. Reddit r/france
Même texte, mais posté **uniquement** dans le fil hebdomadaire ou le format autorisé pour ce type de contenu (les règles de r/france sont strictes sur l'autopromotion).

### 5. LinkedIn (votre profil)
> J'ai lancé salaire-ou-aides.fr, un simulateur pédagogique et sans orientation politique pour répondre à une question qui revient sans cesse : travailler est-il plus intéressant que vivre des aides ?
> Foyer par foyer, il compare le revenu disponible et le reste à vivre, avec ou sans emploi, une fois l'impôt, la santé, le transport, la garde et le loyer comptés. Barèmes 2026, calculs OpenFisca, code source public.
> En bref : le travail paie toujours, mais au SMIC il ne reste qu'environ 3,40 € sur 10 € gagnés, et les écarts vont de +170 € à +700 € par mois selon la situation.
> Chacun peut aussi simuler son propre cas : https://salaire-ou-aides.fr
> Vos retours m'intéressent, en particulier si vous travaillez dans l'action sociale ou l'insertion.

---

## Priorité 3 : relais qui peuvent citer l'outil

### 6. Rubriques de vérification des médias
Elles traitent régulièrement des affirmations du type « au RSA on gagne autant qu'au SMIC ». Le simulateur peut leur servir de source.
- Cibles : Les Décodeurs (Le Monde), CheckNews (Libération), Vrai ou faux (franceinfo), Fake Off (20 Minutes), AFP Factuel.
- Contact : formulaire ou adresse publiée sur chaque rubrique.
- Message :

> Bonjour,
> Vous traitez régulièrement les affirmations sur l'écart entre RSA et SMIC. Je me permets de vous signaler un outil qui pourrait vous servir de source : salaire-ou-aides.fr.
> Il compare, foyer par foyer, le revenu disponible et le reste à vivre avec ou sans emploi, avec les barèmes 2026. Les aides et l'impôt sont calculés avec OpenFisca, et la méthode est entièrement publiée (code source sur GitHub). Le site est indépendant, sans financement ni orientation politique.
> Par exemple : pour une personne seule, environ 965 € par mois sans emploi contre environ 1 570 € au SMIC, après impôt, mutuelle et transport ; mais l'écart tombe à environ 170 € pour quelqu'un qui doit acheter une voiture pour travailler.
> Je reste disponible pour détailler les hypothèses.

### 7. Associations de lutte contre la pauvreté
Elles connaissent le non-recours et la réalité du reste à vivre, et peuvent relayer l'outil auprès des travailleurs sociaux.
- Cibles : ATD Quart Monde, Secours catholique, Fondation pour le logement des défavorisés, UNCCAS (union des CCAS), Fédération des acteurs de la solidarité.
- Message :

> Bonjour,
> J'ai créé un simulateur gratuit et indépendant, salaire-ou-aides.fr, qui montre foyer par foyer ce que rapporte réellement un emploi par rapport aux aides, une fois tous les frais comptés. Il met aussi en évidence le non-recours, la faiblesse du reste à vivre (souvent moins de 10 € par jour et par personne sans emploi) et le coût des frais du travail pour les parents isolés.
> Il pourrait servir aux équipes d'accompagnement pour expliquer une reprise d'emploi, ou dans vos travaux de plaidoyer. Vos retours sur les hypothèses seraient précieux.

### 8. Enseignants de sciences économiques et sociales
- Cible : APSES (association des professeurs de SES), forums et groupes d'enseignants.
- Angle : un outil concret pour étudier la redistribution, les effets de seuil et la notion de taux marginal effectif.

---

## Suivi
Le bilan mensuel automatique (le 3 de chaque mois, dossier `suivi/`) indique les sources de trafic et les nouvelles requêtes : il permet de voir ce qui marche.
