// Calcule les chiffres clés de chaque foyer type avec le modèle de la page (et les données OpenFisca embarquées).
// Usage : node site/compute.js  → JSON sur la sortie standard
const fs = require("fs"), path = require("path");
const html = fs.readFileSync(path.join(__dirname, "..", "travail-vs-aides.html"), "utf8");
const model = html.match(/<script id="model">([\s\S]*?)<\/script>/)[1];
const personas = html.match(/const PERSONAS = (\[[\s\S]*?\n\]);/)[1];
const out = new Function(model + `
  const PERSONAS = ${personas};
  const courantes = h => h.courantes ?? (220 + 80*(h.adults-1) + 45*h.kids.length);
  const alim = h => h.alimBudget ?? (200*h.adults + 130*h.kids.length);
  const rav = (h,x) => x.rd - h.loyer - courantes(h) - alim(h);
  const r = v => Math.round(v);
  const pick = x => ({rd:r(x.rd), net:r(x.net1+(x.net2||0)), pension:r(x.pension||0), rsa:r(x.rsa), pa:r(x.pa), apl:r(x.apl),
    fam:r(x.af+x.cf+x.ab+x.asf), aah:r((x.aah||0)+(x.mva||0)), aspa:r(x.aspa||0), cej:r(x.cej||0),
    frais:r(x.fraisTrajet+x.fraisGarde), sante:r(x.sante+x.rac+x.dep), ir:r(x.ir)});
  return PERSONAS.map(h => { const m = metrics(h);
    return {id:h.id, nom:h.nom, tag:h.tag, desc:h.desc, loyer:h.loyer, persons:h.adults+h.kids.length,
      retraite:!!h.compareRetraite, handicap:!!h.compareHandicap, refS:h.refS||0, ae:!!h.ae,
      base:pick(m.base), full:pick(m.full), gain:r(m.gain), kept10:Math.max(0,(1-m.tme)*10),
      rav0:r(rav(h,m.base)), rav1:r(rav(h,m.full)),
      grid: h.ae ? [500,800,1000,1200,1500,1800,2000,2500,3000].map(S => { const x = simulate(h,S);
        return {ca:S, net:r(x.net1), rsa:r(x.rsa), pa:r(x.pa), apl:r(x.apl), rd:r(x.rd)}; }) : null}; });
`)();
process.stdout.write(JSON.stringify(out));
