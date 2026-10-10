"""Grilles OpenFisca pour chaque foyer : une requête par foyer, un ménage par point de salaire."""
import json, sys, urllib.request, time

API = "https://api.fr.openfisca.org/latest/calculate"
MOIS = [f"{y}-{m:02d}" for y in (2024, 2025, 2026) for m in range(1, 13)]
P = "2026-10"
SMIC = 1867.02

def monthly(v):
    return {m: v for m in MOIS}

# id, adultes, âge, enfants, s2, loyer, commune, options
PERS = [
    ("camille", 1, 38, [], 0, 650, "44109", {}),
    ("bernard", 2, 40, [6, 10], 2880, 950, "44109", {"couple_base": True}),
    ("karim", 1, 30, [], 0, 520, "69123", {}),
    ("sandrine", 1, 41, [8, 13], 0, 470, "42218", {"asf": True}),
    ("moreau", 2, 34, [2, 6], 0, 780, "44109", {}),
    ("diallo", 2, 43, [4, 7, 11, 15], 0, 690, "93066", {}),
    ("nadia", 1, 26, [1], 0, 750, "75056", {"asf": True}),
    ("gerard", 1, 57, [], 0, 380, "23096", {}),
    ("lefevre", 2, 37, [10], SMIC, 650, "67482", {}),
    ("lucas", 1, 22, [], 0, 430, "35238", {}),
    ("sophie", 1, 45, [], 0, 480, "31555", {"aah": True}),
    ("yanis", 1, 31, [], 0, 510, "33063", {"ae": True}),
    ("monique", 1, 67, [], 0, 420, "23096", {"retraite": True}),
]

def build(pid, adults, age, kids, s2, loyer, depcom, opt, points):
    ind, fam, men, ff = {}, {}, {}, {}
    for n, (S, S2, pension) in enumerate(points):
        pre = f"p{n}_"
        parents, enfants = [], []
        for i in range(adults):
            k = pre + f"a{i}"
            d = {"date_naissance": {"ETERNITY": f"{2026-age}-01-15"}}
            sal = S if i == 0 else S2
            if opt.get("ae") and i == 0:
                for y in ("2024", "2025", "2026"):
                    d.setdefault("rpns_micro_entreprise_CA_bic_service_imp", {})[y] = 12 * S
            else:
                d["salaire_de_base"] = monthly(sal)
            if opt.get("aah") and i == 0:
                d["handicap"] = monthly(True); d["taux_incapacite"] = monthly(0.8)
                d["aah"] = {P: None}; d["mva"] = {P: None}
            if opt.get("retraite") and i == 0:
                d["retraite_brute"] = monthly(pension)
            ind[k] = d; parents.append(k)
        for j, a in enumerate(kids):
            k = pre + f"e{j}"
            ind[k] = {"date_naissance": {"ETERNITY": f"{2026-a}-03-01"}}
            enfants.append(k)
        f = {"parents": parents, "enfants": enfants}
        for v in ("rsa", "ppa", "aide_logement", "af", "cf", "asf", "paje_base", "aspa", "bourse_college", "bourse_lycee"):
            f[v] = {P: None}
        f["ars"] = {"2026": None}
        if opt.get("asf"):
            f["asf_elig"] = {P: True} if False else f.get("asf_elig", {P: None})
        fam[pre + "f"] = f
        men[pre + "m"] = {"personne_de_reference": parents[:1], "conjoint": parents[1:], "enfants": enfants,
                          "loyer": monthly(loyer), "statut_occupation_logement": monthly("locataire_vide"),
                          "depcom": monthly(depcom), "cheque_energie": {"2026": None}, "zone_apl": {P: None}}
        ff[pre + "ff"] = {"declarants": parents, "personnes_a_charge": enfants,
                          "impot_revenu_restant_a_payer": {"2026": None}}
    return {"individus": ind, "familles": fam, "menages": men, "foyers_fiscaux": ff}

def call(sit):
    req = urllib.request.Request(API, data=json.dumps(sit).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()[:1500]}

def parse(res, n, opt):
    out = []
    for i in range(n):
        pre = f"p{i}_"
        f = res["familles"][pre + "f"]; m = res["menages"][pre + "m"]; a0 = res["individus"][pre + "a0"]
        g = lambda d, k, per=P: round(d[k][per], 2)
        row = {k: g(f, k) for k in ("rsa", "ppa", "aide_logement", "af", "cf", "asf", "paje_base", "aspa", "bourse_college", "bourse_lycee")}
        row["ars"] = g(f, "ars", "2026")
        row["energie"] = g(m, "cheque_energie", "2026")
        row["zone"] = m["zone_apl"][P]
        row["ir"] = round(-res["foyers_fiscaux"][pre + "ff"]["impot_revenu_restant_a_payer"]["2026"] / 12, 2)
        if opt.get("aah"):
            row["aah"] = g(a0, "aah"); row["mva"] = g(a0, "mva")
        out.append(row)
    return out

if __name__ == "__main__":
    only = sys.argv[1:] or None
    result = {}
    try:
        result = json.load(open("of_data.json"))
    except Exception:
        pass
    for pid, adults, age, kids, s2, loyer, depcom, opt in PERS:
        if only and pid not in only:
            continue
        if opt.get("retraite"):
            points = [(0, 0, 0), (0, 0, 1760)]   # 1 760 € brut ≈ 1 600 € net
            grid = [0, 1]
        else:
            ref = SMIC / (1 - 0.213) if opt.get("ae") else SMIC
            grid = [round(i * 2.5 * ref / 50, 2) for i in range(51)]
            points = [(S, s2, 0) for S in grid]
            if opt.get("couple_base"):
                points.append((0, 0, 0)); grid = grid + ["base"]
        t = time.time()
        res = call(build(pid, adults, age, kids, s2, loyer, depcom, opt, points))
        if "error" in res:
            print(pid, "ERREUR", res["error"][:600]); continue
        result[pid] = {"grid": grid, "rows": parse(res, len(points), opt)}
        r0, r1 = result[pid]["rows"][0], result[pid]["rows"][min(20, len(points) - 1)]
        print(pid, f"{time.time()-t:.0f}s", "zone", r0["zone"], "| S=0", {k: v for k, v in r0.items() if v and k != "zone"}, "| ~1 SMIC", {k: v for k, v in r1.items() if v and k != "zone"})
        json.dump(result, open("of_data.json", "w"))
