"""Seconde relecture d'Assureur B 3.1.6, après les cas de test (DEMARCHE 7.58)."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
p = d["proposition"]
journal = []
TRAVAUX = None
for x in list(p["exclusions_communes"]):
    t = x["texte"]
    if t.startswith("les vols des biens se trouvant à l'extérieur"):
        x["condition"] = {"et": [
            {"ou": [{"f": ["lieu", "jardin"]}, {"f": ["lieu", "terrasse"]}, {"f": ["lieu", "parties_communes"]},
                    {"et": [{"ou": [{"f": ["lieu", "abri_jardin"]}, {"f": ["lieu", "annexe"]}]}, {"f": ["serrure_cylindre", "non"]}]}]},
            {"non": {"ou": [{"f": ["bien", "mobilier_jardin"]}, {"f": ["bien", "plantation"]}]}},
            {"non": {"f": ["lieu", "logement"]}}]}
        journal.append("3.1.6.2.6 : « à l'extérieur » = cours, jardins, terrasse, couloirs et dépendances sans serrure à "
                       "cylindre, à l'adresse du risque ; ni la voie publique ni un autre bâtiment (b-v05, v07, v14)")
journal.append("3.1.6.2.9 inchangé : avec la règle « exclusion entamée » du moteur (7.58), travaux établis et lien "
               "causal inconnu font poser la question ; travaux non évoqués restent une réserve (b-v15)")
d["meta"]["relecture"]["modifications"] += journal
d["meta"]["relecture"]["seconde_passe"] = "après les 15 cas de test Assureur B (regles/cas/golden/assureur-b-habitation-2017.jsonl)"
d.pop("controles", None)
open(dst, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("\n".join(journal))
