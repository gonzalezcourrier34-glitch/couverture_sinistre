"""Le tableau des garanties par formule, lu par la position des mots (DEMARCHE 7.92)."""
import json

from couverture import tableaux


def mot(texte, x0, top):
    return {"text": texte, "x0": x0, "x1": x0 + 6 * len(texte), "top": top}


def test_les_croix_vont_a_la_colonne_la_plus_proche():
    mots = [mot("GARANTIES", 80, 100), mot("ECO", 363, 100), mot("CONFORT", 416, 100), mot("EXCELLENCE", 475, 100),
            mot("Dommages", 80, 120), mot("électriques", 140, 120), mot("X", 431, 120), mot("X", 494, 120),
            mot("Contenu", 80, 134), mot("du", 130, 134), mot("congélateur", 150, 134), mot("X", 494, 134),
            mot("Pack", 80, 148), mot("Jardin", 110, 148), mot("option", 425, 148), mot("option", 488, 148)]
    t = tableaux.lire_mots(mots, ["eco", "confort", "excellence", "privilege"])
    assert t["formules"] == ["eco", "confort", "excellence"]
    assert t["lignes"] == [
        {"libelle": "Dommages électriques", "inclus": ["confort", "excellence"], "option": []},
        {"libelle": "Contenu du congélateur", "inclus": ["excellence"], "option": []},
        {"libelle": "Pack Jardin", "inclus": [], "option": ["confort", "excellence"]}]


def test_une_garantie_plus_large_que_le_tableau_est_un_probleme(tmp_path, monkeypatch):
    monkeypatch.setattr(tableaux, "DOSSIER", tmp_path)
    (tmp_path / "c.json").write_text(json.dumps({
        "formules": ["eco", "confort", "excellence"],
        "lignes": [{"libelle": "Congélateur", "inclus": ["excellence"], "option": []},
                   {"libelle": "Vol", "inclus": ["eco", "confort", "excellence"], "option": []}],
        "correspondance": {"Congélateur": ["congel"], "Vol": ["vol", "vol_cles"]}}), encoding="utf-8")
    pl = ('garantie(congel, "C", \'2.8\', "t").\nperimetre(congel, f(evenement, electricite)).\n'
          'garantie(vol, "V", \'2.5\', "t").\nperimetre(vol, f(evenement, vol)).\n'
          'garantie(vol_cles, "K", \'2.5\', "t").\n'
          'circonstance(vol_cles, ou([f(formule, confort), f(formule, excellence)]), \'2.5\', "t").\n')
    problemes, _ = tableaux.verifier("c", pl)
    assert len(problemes) == 1 and "congel" in problemes[0], "plus étroite que le tableau (vol des clés) : permis"
    pl = pl.replace("perimetre(congel, f(evenement, electricite)).",
                    "perimetre(congel, f(evenement, electricite)).\ncirconstance(congel, f(formule, excellence), '2.8', \"t\").")
    assert tableaux.verifier("c", pl)[0] == []
