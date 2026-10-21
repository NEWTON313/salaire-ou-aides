"""Contenu propre à chaque page par situation : tableau selon le salaire, explications et questions fréquentes.

Les chiffres viennent de compute.js (même modèle et mêmes données OpenFisca que le simulateur).
Utilisé par build_pages.py pour les foyers autres que Karim (RSA ou SMIC) et Yanis (auto-entrepreneur).
"""
import html


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def dec(v):
    return f"{v:.1f}".replace(".", ",")


FRAC = {0.25: "¼ SMIC", 0.5: "½ SMIC", 0.75: "¾ SMIC", 1: "SMIC", 1.25: "1,25 SMIC", 1.5: "1,5 SMIC", 2: "2 SMIC", 2.5: "2,5 SMIC"}

COLS = {"rsa": "RSA", "pa": "Prime d'acti&shy;vité", "apl": "Aide au loge&shy;ment", "fam": "Alloca&shy;tions",
        "aah": "AAH", "cej": "CEJ"}


def row_label(r, d):
    if r["k"] == 0:
        return "Nicolas sans emploi" if d["id"] == "bernard" else "sans emploi"
    if d.get("refS") and abs(r["brut"] - d["refS"]) < 2:
        return "salaire médian"
    return FRAC.get(r["k"], "")


def grid_table(d, cols, first_rows=(), skip=lambda r: False, head="Salaire net"):
    rows = list(first_rows) + [r for r in d["grid"] if not skip(r)]
    body = "\n".join(
        f"<tr><td>{eur(r['net'])} <span class=\"sub\">{html.escape(r.get('label') or row_label(r, d))}</span></td>"
        + "".join(f"<td>{eur(r[c])}</td>" for c in cols) + f"<td><b>{eur(r['rd'])}</b></td></tr>" for r in rows)
    return (f'<div class="scroll"><table class="grid">\n<thead><tr><th>{head}</th>'
            + "".join(f"<th>{COLS[c]}</th>" for c in cols)
            + "<th>Revenu dispo&shy;nible</th></tr></thead>\n<tbody>\n" + body + "\n</tbody></table></div>")


def base_row(d, **extra):
    b = d["base"]
    return {"k": 0, "net": 0, "rsa": b["rsa"], "pa": b["pa"], "apl": b["apl"], "fam": b["fam"], "aah": b["aah"],
            "cej": b["cej"], "rd": b["rd"], **extra}


def g(d, k):
    return next(r for r in d["grid"] if abs(r["k"] - k) < 1e-6)


def why(items, kept):
    lis = "\n".join(f"<li><b>{t}</b> : {txt}</li>" for t, txt in items)
    end = (f"<p>Résultat : sur 10 € de salaire, il reste environ <b>{kept} €</b> de plus à la fin du mois.</p>" if kept else "")
    return f"<ul>\n{lis}\n</ul>\n{end}"


# ---------------------------------------------------------------------------
def sandrine(d):
    b, f = d["base"], d["full"]
    table = grid_table(d, ["rsa", "pa", "apl", "fam"], [base_row(d)], skip=lambda r: r["k"] > 1.5)
    faq = [
        ("Combien touche une mère seule avec 2 enfants au RSA ?",
         f"Sans emploi, avec deux enfants de 8 et 13 ans et un loyer HLM de {eur(d['loyer'])}, Sandrine reçoit environ {eur(b['rsa'])} de RSA, "
         f"{eur(b['apl'])} d'aide au logement et {eur(b['fam'])} de prestations familiales (allocations familiales et allocation de soutien familial). "
         f"Son revenu disponible est de {eur(b['rd'])} par mois."),
        ("Une mère seule a-t-elle droit au RSA majoré ?",
         "Le RSA majoré pour parent isolé n'est versé que pendant 12 mois, dans les 18 mois qui suivent la séparation, "
         "ou jusqu'aux 3 ans du plus jeune enfant. Avec des enfants de 8 et 13 ans et une séparation ancienne, Sandrine touche le RSA ordinaire."),
        ("Qu'est-ce que l'allocation de soutien familial (ASF) ?",
         "Quand l'autre parent ne verse pas de pension alimentaire, la CAF verse l'allocation de soutien familial : 200,78 € par enfant et par mois en 2026. "
         "Elle ne dépend pas des revenus : Sandrine la garde en travaillant."),
        ("Que rapporte un emploi au SMIC à une mère seule ?",
         f"{eur(d['gain'])} de plus par mois dans cet exemple, soit seulement {dec(d['kept10'])} € sur 10 € de salaire. "
         f"Le RSA disparaît, l'aide au logement baisse, et la voiture, les repas et le périscolaire coûtent {eur(f['frais'])} par mois."),
    ]
    body = f"""
<h2>RSA, prime d'activité et allocations selon le salaire</h2>
<p>Mère seule, enfants de 8 et 13 ans, HLM à {eur(d['loyer'])}, voiture (20 km) et périscolaire pour travailler. Montants mensuels 2026, calculés avec OpenFisca.</p>
{table}
<p class="leg">Revenu disponible : salaire et aides, moins l'impôt, la santé, la voiture, les repas et la garde.</p>

<h2>Pourquoi l'emploi rapporte si peu à un parent seul</h2>
{why([("Le RSA disparaît", f"{eur(b['rsa'])} sans emploi, plus rien au SMIC."),
      ("L'aide au logement baisse", f"{eur(b['apl'])} sans emploi, {eur(f['apl'])} au SMIC."),
      ("La prime d'activité compense une partie", f"{eur(f['pa'])} par mois au SMIC."),
      ("Travailler coûte cher", f"voiture, repas et périscolaire : {eur(f['frais'])} par mois.")], dec(d['kept10']))}
<p>Les allocations familiales et l'ASF ({eur(f['fam'])}) restent les mêmes avec ou sans emploi.</p>
"""
    return body, faq


def diallo(d):
    b, f = d["base"], d["full"]
    table = grid_table(d, ["rsa", "pa", "apl", "fam"], [base_row(d)])
    faq = [
        ("Combien d'allocations familiales pour 4 enfants en 2026 ?",
         f"Pour quatre enfants de 4 à 15 ans, la famille Diallo reçoit environ {eur(b['fam'])} par mois de prestations familiales "
         "(allocations familiales et complément familial). Elles ne baissent qu'à partir de revenus plus élevés : "
         f"encore {eur(g(d, 2)['fam'])} avec un salaire de 2 SMIC."),
        ("Combien touche une famille de 4 enfants au RSA ?",
         f"Sans emploi, environ {eur(b['rsa'])} de RSA pour le couple et ses quatre enfants, plus {eur(b['apl'])} d'aide au logement et les prestations familiales. "
         f"Le revenu disponible est de {eur(b['rd'])} par mois."),
        ("Pourquoi la prime d'activité est-elle si élevée pour une famille nombreuse ?",
         f"La prime d'activité augmente avec la taille du foyer. Avec un SMIC, la famille reçoit {eur(f['pa'])} par mois, "
         f"et encore {eur(g(d, 1.5)['pa'])} à 1,5 SMIC."),
        ("Que rapporte un emploi au SMIC à une famille de 4 enfants ?",
         f"{eur(d['gain'])} de plus par mois, soit {dec(d['kept10'])} € sur 10 € de salaire. "
         "Avec un seul salaire, la famille reste largement aidée : prime d'activité, aide au logement et prestations familiales continuent."),
    ]
    body = f"""
<h2>RSA, prime d'activité et allocations selon le salaire</h2>
<p>Couple, quatre enfants de 4 à 15 ans, HLM à {eur(d['loyer'])} en Seine-Saint-Denis. Un seul des deux parents travaille. Montants mensuels 2026, calculés avec OpenFisca.</p>
{table}
<p class="leg">Revenu disponible : salaire et aides, moins l'impôt, la santé, le transport et les repas.</p>

<h2>Ce qui change avec un salaire</h2>
{why([("Le RSA disparaît", f"{eur(b['rsa'])} sans emploi, plus rien au SMIC."),
      ("La prime d'activité prend le relais", f"{eur(f['pa'])} par mois au SMIC."),
      ("L'aide au logement baisse peu", f"{eur(b['apl'])} sans emploi, {eur(f['apl'])} au SMIC."),
      ("Les prestations familiales restent", f"{eur(f['fam'])} par mois.")], dec(d['kept10']))}
"""
    return body, faq


def gerard(d):
    b, f = d["base"], d["full"]
    table = grid_table(d, ["rsa", "pa", "apl"], [base_row(d)])
    faq = [
        ("Combien coûte une voiture pour aller travailler ?",
         "En comptant l'achat d'une occasion, l'assurance, le carburant et l'entretien, une voiture achetée pour travailler revient à environ 0,61 € par kilomètre. "
         f"Pour 40 km par jour, avec les repas, Gérard dépense {eur(f['frais'])} par mois pour aller travailler."),
        ("Travailler au SMIC avec une voiture, est-ce rentable ?",
         f"Oui, mais à peine : {eur(d['gain'])} de plus par mois qu'au RSA dans cet exemple, soit {dec(d['kept10'])} € sur 10 € de salaire. "
         f"À mi-temps, il gagne même moins qu'au RSA : {eur(g(d, 0.5)['rd'])} contre {eur(b['rd'])} sans emploi."),
        ("Les frais de transport sont-ils déduits pour la prime d'activité ?",
         "Non. La prime d'activité est calculée sur le salaire net, sans tenir compte des frais de trajet. "
         "Ils ne réduisent que l'impôt sur le revenu, au-delà de l'abattement forfaitaire de 10 %, ce qui ne joue pas au SMIC."),
        ("Quelles aides pour le transport domicile-travail ?",
         "Selon les régions, des aides existent pour passer le permis ou acheter un véhicule (micro-crédit, aide de France Travail à la mobilité), "
         "et l'employeur peut verser un forfait mobilités durables ou une prime de transport. Elles ne sont pas comptées ici."),
    ]
    body = f"""
<h2>RSA, prime d'activité et revenu selon le salaire</h2>
<p>Personne seule de 57 ans dans la Creuse, loyer de {eur(d['loyer'])}, 40 km aller-retour par jour en voiture, aucun transport en commun. Montants mensuels 2026, calculés avec OpenFisca.</p>
{table}
<p class="leg">Revenu disponible : salaire et aides, moins l'impôt, la santé, la voiture et les repas ({eur(f['frais'])} par mois à temps plein).</p>

<h2>Pourquoi la voiture rend le travail si peu rentable</h2>
{why([("Le RSA et l'aide au logement disparaissent", f"{eur(b['rsa'] + b['apl'])} par mois sans emploi, plus rien au SMIC."),
      ("La prime d'activité compense une partie", f"{eur(f['pa'])} par mois au SMIC."),
      ("La voiture coûte presque autant", f"{eur(f['frais'])} par mois avec les repas, soit plus d'un tiers du SMIC net.")], dec(d['kept10']))}
"""
    return body, faq


def lucas(d):
    b, f, a = d["base"], d["full"], d["apresCej"]
    table = grid_table(d, ["cej", "pa", "apl"],
                       [base_row(d, label="sans emploi, en CEJ"),
                        {"k": 0, "net": 0, "cej": 0, "pa": 0, "apl": a["apl"], "rd": a["rd"], "label": "sans emploi, après le CEJ"}],
                       skip=lambda r: r["k"] < 1)
    faq = [
        ("Peut-on toucher le RSA avant 25 ans ?",
         "En général non. Le RSA est ouvert avant 25 ans seulement aux parents (ou futurs parents) et aux jeunes ayant travaillé l'équivalent de deux ans à temps plein "
         "au cours des trois dernières années (RSA jeune actif)."),
        ("Combien rapporte le contrat d'engagement jeune (CEJ) ?",
         f"Jusqu'à 566,17 € par mois en 2026 pour un jeune de 18 à 25 ans détaché de sa famille, pendant 12 mois en général, contre 15 à 20 heures d'activités par semaine. "
         f"Avec l'aide au logement, Lucas dispose de {eur(b['rd'])} par mois. Après le contrat, sans emploi, il ne lui reste que {eur(a['rd'])}."),
        ("Un jeune de moins de 25 ans a-t-il droit à la prime d'activité ?",
         f"Oui, dès 18 ans, comme les autres actifs. Au SMIC, Lucas reçoit {eur(f['pa'])} de prime d'activité."),
        ("Que rapporte un emploi au SMIC à un jeune ?",
         f"{eur(f['rd'])} de revenu disponible au SMIC, soit {eur(d['gain'])} de plus que pendant le CEJ, et {eur(f['rd'] - a['rd'])} de plus qu'une fois le CEJ terminé. "
         "Pour un jeune, l'écart entre emploi et absence d'emploi est l'un des plus élevés."),
    ]
    body = f"""
<h2>CEJ, prime d'activité et aide au logement selon le salaire</h2>
<p>Jeune de 22 ans, seul dans un studio à {eur(d['loyer'])} à Rennes, transports en commun. Montants mensuels 2026, calculés avec OpenFisca.</p>
{table}
<p class="leg">Revenu disponible : salaire et aides, moins l'impôt, la santé, le transport et les repas.</p>

<h2>Pourquoi l'emploi rapporte beaucoup avant 25 ans</h2>
{why([("Pas de RSA", "sans enfant, Lucas n'y a pas droit : le filet de sécurité est le CEJ, limité dans le temps."),
      ("Après le CEJ, il ne reste que l'aide au logement", f"{eur(a['rd'])} de revenu disponible par mois."),
      ("La prime d'activité s'ajoute au salaire", f"{eur(f['pa'])} par mois au SMIC.")], dec(d['kept10']))}
"""
    return body, faq


def sophie(d):
    b, f = d["base"], d["full"]
    table = grid_table(d, ["aah", "pa", "apl"], [base_row(d, label="sans emploi")], skip=lambda r: r["k"] > 1.5)
    q1 = g(d, 0.25)
    faq = [
        ("Quel est le montant de l'AAH en 2026 ?",
         "L'allocation aux adultes handicapés est de 1 041,59 € par mois à taux plein. Depuis octobre 2023, les revenus du conjoint ne sont plus pris en compte. "
         "Une personne qui ne travaille pas et vit dans un logement indépendant peut aussi recevoir la majoration pour la vie autonome (104,77 €)."),
        ("Peut-on cumuler l'AAH et un salaire ?",
         "Oui. Pendant les six premiers mois d'une reprise d'emploi, le salaire n'est pas compté. Ensuite, l'AAH baisse, mais une partie du salaire est neutralisée : "
         "80 % de la part inférieure à 30 % du SMIC brut, puis 40 % au-delà. "
         f"Avec un quart de SMIC ({eur(q1['net'])} net), l'AAH reste d'environ {eur(q1['aah'])}."),
        ("Jusqu'à quel salaire garde-t-on l'AAH ?",
         f"Pour une personne seule, l'AAH s'éteint un peu au-delà de 1,25 SMIC : encore {eur(g(d, 1)['aah'])} au SMIC, {eur(g(d, 1.25)['aah'])} à 1,25 SMIC, plus rien à 1,5 SMIC."),
        ("Le niveau de vie à l'AAH est-il proche de celui d'un salarié au SMIC ?",
         f"Dans cet exemple, oui : {eur(b['rd'])} par mois avec l'AAH, contre {eur(f['rd'])} pour une personne valide au SMIC dans le même logement, "
         f"soit un écart de {eur(d['gain'])}. Mais une personne à l'AAH a souvent des frais liés au handicap qui ne sont pas comptés ici."),
    ]
    body = f"""
<h2>AAH et salaire : ce qui reste selon le revenu</h2>
<p>Personne seule à Toulouse, loyer de {eur(d['loyer'])}, taux d'incapacité de 80 %, après les six premiers mois d'emploi. Montants mensuels 2026, calculés avec OpenFisca.
Ce tableau vaut pour les personnes à l'AAH qui peuvent travailler un peu ; Sophie, elle, ne le peut pas.</p>
{table}
<p class="leg">Revenu disponible : salaire et aides, moins l'impôt, la santé et le transport. Sans emploi, l'AAH comprend la majoration pour la vie autonome.</p>
"""
    return body, faq


def monique(d):
    b, f = d["base"], d["full"]
    faq = [
        ("Quel est le montant du minimum vieillesse (ASPA) en 2026 ?",
         "L'allocation de solidarité aux personnes âgées garantit 1 043,59 € par mois à une personne seule, et 1 620,18 € à un couple. "
         "Elle est versée à partir de 65 ans (ou de l'âge légal en cas d'inaptitude) et complète les autres ressources jusqu'à ce montant."),
        ("Le minimum vieillesse est-il récupéré sur la succession ?",
         "Oui, les sommes versées peuvent être récupérées sur la part de la succession qui dépasse un seuil d'actif net (environ 100 000 € en métropole). "
         "Un petit patrimoine n'est donc pas concerné."),
        ("Quelle différence entre le minimum vieillesse et une retraite au salaire médian ?",
         f"Dans cet exemple, {eur(b['rd'])} par mois au minimum vieillesse (avec l'aide au logement), contre {eur(f['rd'])} avec une retraite de 1 600 € après 43 ans au salaire médian, "
         f"soit {eur(d['gain'])} d'écart. La retraitée perd l'aide au logement et paie une mutuelle senior plus chère."),
        ("Pourquoi l'écart est-il si faible ?",
         f"Parce que le minimum vieillesse ({eur(b['aspa'])}) s'accompagne d'une aide au logement ({eur(b['apl'])}) et de la complémentaire santé solidaire, "
         "alors qu'une retraite de 1 600 € n'ouvre plus droit à ces aides. L'écart de niveau de vie ne reflète pas l'écart de cotisations sur une carrière entière."),
    ]
    body = f"""
<h2>Ce qui fait l'écart entre les deux retraites</h2>
{why([("Le minimum vieillesse", f"{eur(b['aspa'])} par mois sans aucune carrière."),
      ("L'aide au logement", f"{eur(b['apl'])} au minimum vieillesse, {eur(f['apl'])} avec une retraite de 1 600 €."),
      ("La santé", f"{eur(b['sante'])} par mois au minimum vieillesse grâce à la complémentaire santé solidaire, {eur(f['sante'])} avec une mutuelle senior.")], None)}
"""
    return body, faq


def camille(d):
    b, f = d["base"], d["full"]
    table = grid_table(d, ["rsa", "pa", "apl"], skip=lambda r: r["k"] == 0, first_rows=[base_row(d)])
    faq = [
        ("Quel est le salaire médian en France ?",
         "Dans le secteur privé, la moitié des salariés à temps plein gagne moins d'environ 2 880 € brut par mois, et l'autre moitié plus. "
         "C'est le salaire médian retenu ici, bien au-dessus du SMIC (1 867,02 € brut en 2026)."),
        ("Combien gagne-t-on de plus au salaire médian qu'en vivant des aides ?",
         f"Pour une personne seule, {eur(f['rd'])} de revenu disponible au salaire médian, contre {eur(b['rd'])} sans emploi : "
         f"{eur(d['gain'])} de plus par mois, soit environ deux fois plus, une fois la voiture, la mutuelle et l'impôt payés."),
        ("Touche-t-on la prime d'activité au salaire médian ?",
         f"Non, pas pour une personne seule : la prime s'arrête vers 1,5 SMIC. Elle est de {eur(g(d, 1)['pa'])} au SMIC, et nulle au salaire médian."),
        ("Combien d'impôt sur le revenu au salaire médian ?",
         f"Environ {eur(f['ir'])} par mois pour une personne seule sans enfant, après l'abattement de 10 % pour frais professionnels."),
    ]
    body = f"""
<h2>Revenu disponible selon le salaire</h2>
<p>Personne seule, loyer de {eur(d['loyer'])}, voiture (15 km) pour aller travailler. Montants mensuels 2026, calculés avec OpenFisca.</p>
{table}
<p class="leg">Revenu disponible : salaire et aides, moins l'impôt, la santé, la voiture et les repas.</p>

<h2>Ce qui change au salaire médian</h2>
{why([("Plus d'aides", f"ni RSA, ni prime d'activité, ni aide au logement ({eur(b['rsa'] + b['apl'])} par mois sans emploi)."),
      ("L'impôt apparaît", f"{eur(f['ir'])} par mois."),
      ("Les frais du travail", f"voiture et repas : {eur(f['frais'])} par mois.")], dec(d['kept10']))}
"""
    return body, faq


def bernard(d):
    b, f = d["base"], d["full"]
    table = grid_table(d, ["pa", "apl", "fam"], [base_row(d, label="les deux sans emploi")], head="Salaire net de Nicolas")
    z = g(d, 0)
    faq = [
        ("Un couple avec deux salaires médians a-t-il droit à des aides ?",
         f"Peu : ni RSA, ni prime d'activité, ni aide au logement. Il garde les allocations familiales pour deux enfants ({eur(f['fam'])} par mois), "
         "qui ne dépendent quasiment pas des revenus à ce niveau."),
        ("Que perd un couple quand l'un des deux arrête de travailler ?",
         f"Si Nicolas n'a plus d'emploi et qu'Émilie reste au salaire médian, le foyer passe de {eur(f['rd'])} à {eur(z['rd'])} par mois : "
         f"la prime d'activité ({eur(z['pa'])}) et l'aide au logement ({eur(z['apl'])}) compensent une partie de la perte."),
        ("Combien d'impôt paie un couple avec deux salaires médians et 2 enfants ?",
         f"Environ {eur(f['ir'])} par mois, grâce aux trois parts du quotient familial."),
        ("Que rapportent deux emplois par rapport aux aides ?",
         f"{eur(f['rd'])} de revenu disponible par mois avec deux salaires médians, contre {eur(b['rd'])} si aucun des deux ne travaille : "
         f"{eur(d['gain'])} de plus, une fois les deux voitures, le périscolaire et l'impôt payés."),
    ]
    body = f"""
<h2>Revenu du foyer selon le salaire de Nicolas</h2>
<p>Couple, deux enfants de 6 et 10 ans, loyer de {eur(d['loyer'])} près de Nantes. Émilie gagne le salaire médian ; on fait varier le salaire de Nicolas. Montants mensuels 2026, calculés avec OpenFisca.</p>
{table}
<p class="leg">Revenu disponible : salaires et aides, moins l'impôt, la santé, les deux voitures, les repas et le périscolaire.</p>
"""
    return body, faq


BLOCKS = {"sandrine": sandrine, "diallo": diallo, "gerard": gerard, "lucas": lucas, "sophie": sophie,
          "monique": monique, "camille": camille, "bernard": bernard}


def block(d):
    """Renvoie (html, json-ld FAQPage) pour un foyer, ou ("", None) s'il n'a pas de contenu propre."""
    fn = BLOCKS.get(d["id"])
    if not fn:
        return "", None
    body, faq = fn(d)
    body += "\n<h2>Questions fréquentes</h2>\n" + "\n".join(f"<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return body, ld
