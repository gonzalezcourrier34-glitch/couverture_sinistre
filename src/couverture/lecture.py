"""La lecture : le modèle traduit une déclaration en faits du vocabulaire commun, sans rien décider.

Le modèle ne décide rien et ne cite rien : il traduit la déclaration en une dizaine de faits (« lieu =
parties_communes », « effraction = oui »), et laisse inconnu ce que la déclaration ne dit pas. Le code ramène
ensuite ces faits au vocabulaire (préciser, impliquer, filtrer).
"""

from __future__ import annotations


from . import prolog
from .llm import LLM, ErreurLLM, completer_avec_schema, extraire_json

# --- Lecture en deux temps (DEMARCHE 7.38) ----------------------------------------------------------------
#  Avec tout le vocabulaire d'un coup, Mistral Small oubliait des faits à mesure que la liste s'allongeait
#  (7.32). Temps 1 : ce qui s'est passé, quoi, où. Temps 2 : seulement les questions qui concernent cet
#  événement (« pour » dans le vocabulaire). Puis une vérification, fait par fait (7.43 à 7.45). La lecture en
#  un temps et la lecture en parallèle, essayées et écartées (7.38 à 7.42), ont été retirées le 20 nov. 2026.

SOCLE = ("evenement", "bien", "lieu")

REGLES_COMMUNES = """- N'utilise que les variables et les valeurs de la liste. Une variable marquée « plusieurs » prend une liste ; les autres, une seule valeur.
- Ne renseigne une variable que si la déclaration la dit ou l'implique clairement. Sinon, réponds "inconnu" (ou une liste vide) : elle restera inconnue, et le gestionnaire posera la question. Un fait inventé est plus grave qu'un fait manquant.
- « inconnu » est la réponse normale pour la plupart des variables : une déclaration ne dit presque jamais tout. Ne choisis pas « non », « aucune » ou « tiers » par défaut : seulement si c'est écrit."""

SYSTEME_LECTURE_SOCLE = """Tu lis la déclaration d'un sinistre et tu dis ce qui s'est passé, ce qui est touché et où, avec un vocabulaire imposé. Tu ne décides pas si le sinistre est couvert.

Le vocabulaire donne, pour chaque variable, la question à laquelle elle répond, ses valeurs, et le sens des valeurs proches. Choisis la valeur dont le sens correspond à ce qui est écrit.

Règles :
""" + REGLES_COMMUNES + """
- evenement : la cause, et aussi le dommage s'il est d'une autre nature. Une tempête qui arrache des tuiles et fait entrer la pluie : ["tempete", "degat_eaux"]. Ne perds jamais la cause, même si aucune valeur ne la nomme exactement : prends la plus proche par son sens, ou « autre ».
- « Disparu », « je ne retrouve plus » ne disent pas qu'il y a eu vol : ne mets evenement = vol que si un vol est décrit (volé, pris, cambriolé, arraché).
- Un lieu se déduit de ce qui est écrit : une pièce ou une partie du logement (salon, cuisine, salle de bain, entrée, parquet, plafond, « chez moi », « mon appartement ») donne lieu = logement. Mais ce qui ne dit rien de l'endroit ne donne pas de lieu : « pendant que je faisais mes courses » ne dit pas où était le vélo.
- Façade, murs, parquet, plafond, toiture : bien = element_batiment. Tuyau, canalisation : bien = canalisation.
- bien : ce qui a été volé, perdu ou abîmé. Des clés seulement si ce sont elles qui ont été volées ou perdues : la clé dont le voleur s'est servi (sous le paillasson, dans la boîte aux lettres) n'est pas un bien volé.

Réponds uniquement par un objet JSON : {"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}}"""

SYSTEME_LECTURE_DETAILS = """Tu lis la déclaration d'un sinistre et tu réponds à quelques questions précises, avec un vocabulaire imposé. Ce qui s'est passé, ce qui est touché et où sont déjà établis : ne les répète pas. Tu ne décides pas si le sinistre est couvert.

Le vocabulaire donne, pour chaque variable, la question à laquelle elle répond, ses valeurs, et le sens des valeurs proches. Choisis la valeur dont le sens correspond à ce qui est écrit.

Règles :
""" + REGLES_COMMUNES + """
- N'ajoute jamais une absence, des portes ou des fenêtres fermées, un auteur ou une cause qui ne sont pas écrits.
- Ne renseigne pas une variable sans rapport avec ce qui s'est passé.
- « fermé à clé » sans autre précision : fermeture = cle, et ne renseigne pas serrure_surete.
- Des flammes qui brûlent ou se propagent à d'autres objets : flammes = oui et embrasement = oui. « Avec la chaleur » sans flamme décrite : flammes = non.
- Une durée dite se traduit : déposé « il y a deux semaines » donne depot_moins_30j = oui.
- Les précautions décrites se traduisent : une fenêtre laissée ouverte donne fenetres_fermees = non ; un chauffage coupé pendant le gel, sans vidange ni isolation, donne prevention_gel = non.

Réponds uniquement par un objet JSON : {"faits": {"variable": "valeur"}}"""


INCONNU = "inconnu"


SYSTEME_DECOUPAGE = """Tu lis une déclaration de sinistre en assurance habitation et tu dis combien de sinistres distincts elle contient.

Un sinistre, c'est un fait générateur et tout ce qu'il a entraîné. Une cause et ses conséquences font UN seul sinistre :
- une tempête arrache des tuiles et la pluie entre : un sinistre ;
- une fuite abîme un parquet, puis des moisissures apparaissent : un sinistre ;
- un cambriolage, avec la porte forcée, les objets volés et ce qui a été abîmé : un sinistre ;
- un incendie et les dégâts de l'eau des pompiers : un sinistre.

Il y a plusieurs sinistres quand des faits générateurs indépendants sont racontés ensemble : un vol, et par ailleurs une vitre fêlée dont on ne sait pas l'origine ; une fuite, et un autre jour un objet cassé.

Règles :
- dans le doute, un seul sinistre ;
- pour chaque sinistre, un titre court dans les mots de la déclaration, et les phrases de la déclaration qui le concernent, recopiées mot pour mot, sans rien ajouter ni reformuler ;
- les phrases de contexte qui valent pour plusieurs sinistres (une absence, le lieu, une plainte) se recopient dans chacun de ceux qu'elles concernent ;
- quand la déclaration dit ne pas savoir si deux faits sont liés, recopie cette phrase dans chacun des deux.

Réponds en JSON : {"sinistres": [{"titre": "...", "phrases": ["...", "..."]}]}"""

SCHEMA_DECOUPAGE = {"type": "object", "additionalProperties": False, "required": ["sinistres"], "properties": {
    "sinistres": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                             "required": ["titre", "phrases"], "properties": {
                                                 "titre": {"type": "string"},
                                                 "phrases": {"type": "array", "items": {"type": "string"}}}}}}}


def decouper_sinistres(sinistre: str, llm: LLM) -> list[dict]:
    """Les sinistres distincts d'une déclaration (7.168) : [{"titre", "texte"}], ou [] s'il n'y en a qu'un.

    Le modèle recopie pour chaque sinistre les phrases qui le concernent ; le code ne garde que celles qui figurent
    mot pour mot dans la déclaration (le même garde-fou que pour les citations du contrat). Un sinistre sans phrase
    retrouvée est écarté ; à moins de deux sinistres restants, la déclaration se traite d'un bloc, comme avant."""
    from .texte import normaliser
    reponse = extraire_json(completer_avec_schema(llm, SYSTEME_DECOUPAGE, f"## Déclaration\n{sinistre}", SCHEMA_DECOUPAGE))
    entier = normaliser(sinistre)
    parties = []
    for s in (reponse.get("sinistres") or []) if isinstance(reponse, dict) else []:
        if not isinstance(s, dict):
            continue
        phrases = [p.strip() for p in s.get("phrases") or [] if isinstance(p, str) and p.strip()
                   and normaliser(p) in entier]
        if phrases:
            parties.append({"titre": str(s.get("titre") or "").strip() or f"Sinistre {len(parties) + 1}",
                            "texte": " ".join(dict.fromkeys(phrases))})
    return parties if len(parties) >= 2 else []


def schema_faits(variables: dict) -> dict:
    """Le schéma JSON de la réponse : chaque variable avec ses seules valeurs permises (listes fermées),
    « inconnu » en premier. **Aucune variable n'est obligatoire** : quand le schéma les exigeait toutes,
    Mistral Small remplissait au lieu de laisser vide (« fermeture = aucune » pour « volé dans ma cave »),
    avec null en fin de liste (7.38) comme avec « inconnu » en tête (7.39). La lecture d'un seul coup, sans
    schéma, ne le faisait pas : le modèle n'écrivait que ce qu'il avait trouvé."""
    proprietes = {}
    for v, d in variables.items():
        if d.get("plusieurs"):
            proprietes[v] = {"type": "array", "items": {"type": "string", "enum": list(d["valeurs"])}}
        else:
            proprietes[v] = {"type": "string", "enum": [INCONNU] + list(d["valeurs"])}
    return {"type": "object", "additionalProperties": False, "required": ["faits"],
            "properties": {"faits": {"type": "object", "additionalProperties": False, "properties": proprietes}}}


def _lire(llm: LLM, systeme: str, variables: dict, message: str) -> dict:
    liste = "\n".join(description_variable(v, d) for v, d in variables.items())
    texte = completer_avec_schema(llm, systeme, f"## Vocabulaire\n{liste}\n\n{message}", schema_faits(variables))
    lus = {}
    for v, x in (extraire_json(texte).get("faits") or {}).items():
        x = [e for e in x if e != INCONNU] if isinstance(x, list) else (None if x == INCONNU else x)
        if x not in (None, "", []):
            lus[v] = x
    return lus


SYSTEME_VERIFICATION = """Tu relis la déclaration d'un sinistre et tu vérifies des affirmations qu'un collègue en a tirées. Tu ne décides pas si le sinistre est couvert.

Pour chaque affirmation, réponds :
- "dit" si la déclaration l'affirme, ou l'implique sans aucun doute ;
- "non_dit" si la déclaration ne le dit pas : elle n'en parle pas, ou il faudrait le supposer.

Une affirmation plausible mais non écrite est "non_dit". Exemples : « le local n'était pas fermé » pour « on m'a volé mon vélo dans ma cave » est non_dit (la déclaration ne dit rien de la fermeture) ; « l'assuré était absent » pour « pendant mes vacances » est dit.

Une réponse « non » compte comme le reste : elle est "dit" quand la négation est écrite en toutes lettres (« aucune effraction », « personne n'a été menacé », « sans flammes »), ou quand un détail écrit correspond au sens donné entre parenthèses pour « non ». Exemples : « fermée par un simple cadenas » pour une serrure de sûreté → non (cadenas…) est dit ; « on me l'a pris sans que je m'en rende compte » pour des violences → non (aucun contact ni menace…) est dit.

Pour toute autre valeur, un mot commun ne suffit pas : vérifie que ce qui est écrit correspond au sens de la valeur, y compris ce que ce sens écarte. « L'eau de la machine à laver s'est infiltrée dans le plancher » pour une infiltration extérieure (pluie entrée par un mur…) est non_dit : l'eau vient de l'intérieur, pas de dehors.

Réponds uniquement par un objet JSON : {"verdicts": {"variable": "dit"}}"""


def affirmation(v: str, x, voc: dict) -> str:
    """Un fait lu, en phrase à vérifier : la question du vocabulaire et la valeur, avec son sens s'il est donné."""
    aide = voc.get(v, {}).get("aide", {})
    valeurs = x if isinstance(x, list) else [x]
    rendu = ", ".join(f"{e} ({aide[e]})" if e in aide else str(e) for e in valeurs)
    return f"- {v} : {voc.get(v, {}).get('question', v)} → {rendu}"


def juger_affirmations(sinistre: str, faits: dict, llm: LLM, voc: dict) -> dict:
    """{variable: "dit" | "non_dit"} : chaque fait soumis au modèle comme une affirmation sur la déclaration."""
    liste = "\n".join(affirmation(v, x, voc) for v, x in faits.items())
    schema = {"type": "object", "additionalProperties": False, "required": ["verdicts"],
              "properties": {"verdicts": {"type": "object", "additionalProperties": False,
                                          "properties": {v: {"type": "string", "enum": ["dit", "non_dit"]} for v in faits}}}}
    return extraire_json(completer_avec_schema(
        llm, SYSTEME_VERIFICATION, f"## Affirmations\n{liste}\n\n## Déclaration\n{sinistre}", schema)).get("verdicts") or {}


def faits_decisifs(faits: dict, decideur, decision: str) -> list[str]:
    """Les faits qui portent la décision : ceux dont le retrait la change. Le moteur le dit en quelques
    millisecondes ; ce sont eux qu'une réponse ferme doit avoir confirmés (7.49)."""
    return [v for v in faits if decideur({k: x for k, x in faits.items() if k != v})["decision"] != decision]


def verifier_details(sinistre: str, lus: dict, llm: LLM, voc: dict) -> tuple[dict, list[str]]:
    """Le contrôle des faits du temps 2. Les faits du socle (événement, bien, lieu) ne sont pas soumis : retirés,
    ils rendaient tout incertain (7.26). Une vérification illisible ne retire rien (avertissement)."""
    details = {v: x for v, x in lus.items() if v not in SOCLE and x not in (None, "", [])}
    if not details:
        return lus, []
    try:
        verdicts = juger_affirmations(sinistre, details, llm, voc)
    except ErreurLLM:
        raise
    except Exception as e:  # noqa: BLE001
        return lus, [f"vérification des faits illisible ({e}) : faits gardés"]
    gardes, retires = dict(lus), []
    for v, x in details.items():
        if verdicts.get(v) == "non_dit":
            del gardes[v]
            retires.append(f"{v} = {x if not isinstance(x, list) else '/'.join(x)} : non dit dans la déclaration, retiré")
    return gardes, retires


def variables_du_temps_2(voc: dict, evenements: list[str], socle: dict | None = None) -> dict:
    """Les variables à demander une fois l'événement connu : celles qui s'y appliquent (« pour »), et celles
    qui s'appliquent à tout. Sans événement lu, toutes. Une variable d'extension (« si » : le lieu qui
    l'entame, 7.70) est demandée aussi quand le temps 1 a lu ce lieu : le séjour temporaire pour un « autre
    bâtiment », pas pour chaque sinistre au logement."""
    ev = set(evenements)

    def entamee(d):
        return any(set(x if isinstance(x, list) else [x]) & set(vals)
                   for var, vals in (d.get("si") or {}).items() for x in [(socle or {}).get(var) or []])

    def hors_lieu(d):
        # « seulement_si » (7.71) : une variable du véhicule ne se lit pas quand le lieu lu est la cave. Lieu non lu :
        # on la garde, faute de savoir.
        lus = {var: set(x if isinstance(x, list) else [x]) for var, x in (socle or {}).items() if x}
        return any(var in lus and not lus[var] & set(vals) for var, vals in (d.get("seulement_si") or {}).items())

    # « jamais » (7.90) : la réserve d'une exclusion que l'assureur prouve (une option, une rixe) ; pas lue.
    return {v: d for v, d in voc.items() if v not in SOCLE and d.get("pour") != ["jamais"]
            and (not ev or not d.get("pour") or ev & set(d["pour"]) or entamee(d)) and not hors_lieu(d)}


def variables_du_contrat(contrat_id: str) -> set[str] | None:
    """Les variables que les règles du contrat emploient (`f(variable, …)`), ou None sans fichier de règles.
    Le vocabulaire est commun à tous les assureurs ; un contrat n'en lit que ce qu'il emploie (7.57)."""
    if not prolog.fichier_regles(contrat_id).exists():
        return None
    employees = prolog.variables_employees(contrat_id)
    # Une variable qui implique un fait employé se lit aussi (7.101) : « la porte était ouverte » (`acces_voleur =
    # sans_effraction`) dit l'absence d'effraction, que la déclaration n'écrit jamais en ces termes.
    return employees | {v for v, d in prolog.vocabulaire().items()
                        if any(var in employees for faits in (d.get("implique") or {}).values() for var in faits)}


def extraire_faits_regles(sinistre: str, llm: LLM, decideur=None, variables: set[str] | None = None,
                          exemples=None, verifier: bool = True, llm_socle: LLM | None = None,
                          suivi=None, llm_verification: LLM | None = None,
                          voc: dict | None = None) -> tuple[dict, list[str]]:
    """Les faits lus par le modèle, et les écarts au vocabulaire (retirés). Deux temps (le socle, puis les
    questions de cet événement), puis la vérification fait par fait (`verifier=False` : sans, pour les tests).
    `decideur(faits) -> dict` (le moteur) arbitre la vérification (7.44).
    `variables` : celles du contrat (le socle est toujours lu) ; None : tout le vocabulaire.
    `voc` : le vocabulaire tel que le contrat le voit (`prolog.vocabulaire_du_contrat`) ; None : le vocabulaire entier.
    `exemples(evenement=None) -> [exemple]` : des déclarations proches et leurs faits, montrés au socle puis aux
    détails (ceux du même événement) (7.108). None : pas d'exemples.
    `llm_socle` : un autre modèle pour le seul temps 1 (7.118) ; None : le même.
    `llm_verification` : un autre modèle pour vérifier les faits lus (7.136) ; None : le même.
    `suivi(etape, detail=None)` : appelé au début de chaque étape (sans détail), puis à sa fin avec ce qu'elle a
    donné, en une phrase : pour montrer l'analyse pendant qu'elle se fait (7.134). None : rien."""
    dire = suivi or (lambda etape, detail=None: None)

    def en_clair(faits: dict) -> str:
        return " ; ".join(f"{v.replace('_', ' ')} : {', '.join(str(e).replace('_', ' ') for e in (x if isinstance(x, list) else [x]))}"
                          for v, x in faits.items() if x not in (None, "", []))

    from .exemples import bloc

    voc = voc if voc is not None else prolog.vocabulaire()
    if variables is not None:
        # Les règles d'Assureur B ne doivent pas changer ce qu'on lit pour Assureur A : la plainte ou la formule
        # « Privilège » n'ont rien à faire dans la lecture d'un vol chez Assureur A (7.57).
        voc = {v: d for v, d in voc.items() if v in SOCLE or v in variables}
    declaration = f"## Déclaration\n{sinistre}"
    # Pas d'exemples au socle (7.116) : Small y recopiait les biens et les événements des exemples (le congélateur
    # d'un exemple ajoutait des denrées, la chaudière d'un autre l'assistance), et le socle n'est pas vérifié. Au
    # temps 2, chaque fait recopié passe par la vérification.
    dire("socle")
    lus = _lire(llm_socle or llm, SYSTEME_LECTURE_SOCLE, {v: voc[v] for v in SOCLE}, declaration)
    # L'événement précisé avant de choisir les questions du temps 2 : un « accident » sur un miroir est un bris
    # (7.86), et c'est pour le bris qu'on demande si le miroir était posé (7.113). Précisé après, trop tard : le
    # temps 2 posait les questions de l'« accident », qui n'en a pas.
    lus = preciser(lus, voc)[0]
    dire("socle", en_clair(lus) or "rien de reconnu dans la déclaration")
    evenements = [str(e) for e in (lus.get("evenement") or []) if str(e) in voc["evenement"]["valeurs"]]
    details = variables_du_temps_2(voc, evenements, lus)
    dire("details")
    if details:
        etabli = "; ".join(f"{v} = {'/'.join(map(str, x)) if isinstance(x, list) else x}"
                           for v, x in lus.items() if x not in (None, "", []))
        ex_details = bloc(exemples(evenements[0] if evenements else None), details) if exemples else ""
        lus |= {v: x for v, x in _lire(llm, SYSTEME_LECTURE_DETAILS, details,
                                       f"{ex_details}## Déjà établi\n{etabli or 'rien'}\n\n{declaration}").items()
                if v not in SOCLE}
    lus_details = {v: x for v, x in lus.items() if v not in SOCLE}
    dire("details", en_clair(lus_details) or "aucun détail dit dans la déclaration")
    if not verifier:
        return au_vocabulaire(lus, voc)
    dire("verification")
    lus_verifies, retraits = verifier_details(sinistre, lus, llm_verification or llm, voc)
    non_dits = [r.split(" : ")[0].replace("_", " ") for r in retraits if "non dit" in r]
    dire("verification", ("retiré, car non dit dans la déclaration : " + " ; ".join(non_dits)) if non_dits
         else "chaque fait est bien dans la déclaration")
    faits, ecarts = au_vocabulaire(lus_verifies, voc)
    if decideur is not None and any("non dit" in r for r in retraits):
        # Un doute ne doit jamais faire couvrir : si retirer les faits « non dits » fait passer la décision à
        # « couvert », la vérification a sans doute écarté un fait vrai qui faisait refuser (la fenêtre laissée
        # ouverte, le chauffage coupé : 7.44). Le moteur tranche : on garde alors la lecture non vérifiée.
        faits_lus, ecarts_lus = au_vocabulaire(lus, voc)
        if decideur(faits)["decision"] == "COUVERT" and decideur(faits_lus)["decision"] != "COUVERT":
            return faits_lus, ecarts_lus + ["vérification écartée : retirer ces faits aurait fait couvrir ("
                                            + "; ".join(r.split(" : ")[0] for r in retraits) + ")"]
    return faits, retraits + ecarts


def au_vocabulaire(lus: dict, voc: dict) -> tuple[dict, list[str]]:
    """Les faits lus, ramenés au vocabulaire : variables et valeurs inconnues retirées, faits hors sujet retirés."""
    faits, ecarts = {}, []
    for v, x in lus.items():
        if x in (None, "", []):
            continue
        valeurs = [str(e) for e in (x if isinstance(x, list) else [x])]
        if v not in voc:
            ecarts.append(f"variable inconnue ignorée : {v}")
            continue
        bonnes = [e for e in valeurs if e in voc[v]["valeurs"]]
        ecarts += [f"{v} = {e} : valeur hors vocabulaire, ignorée" for e in valeurs if e not in bonnes]
        if bonnes:
            faits[v] = bonnes if voc[v].get("plusieurs") else bonnes[0]
    faits, precises = preciser(faits, voc)
    faits, impliques = impliquer(faits, voc)
    faits, retires = prolog.filtrer_faits(faits, voc)
    return faits, ecarts + precises + impliques + retires


def sources_impliquees(faits: dict, voc: dict) -> dict[str, str]:
    """{fait déduit : le fait lu qui le dit}, pour les faits que « implique » donne (7.95)."""
    sources = {}
    for v, regles in ((v, d.get("implique")) for v, d in voc.items() if d.get("implique")):
        valeurs = faits.get(v)
        for x in valeurs if isinstance(valeurs, list) else [valeurs]:
            for w, y in (regles.get(x) or {}).items():
                lu = faits.get(w)
                if lu == y or (isinstance(lu, list) and y in lu):
                    sources[w] = v
    return sources


def impliquer(faits: dict, voc: dict) -> tuple[dict, list[str]]:
    """Un fait qui en dit un autre (vocabulaire, clé « implique ») : « entré sans effraction, porte non
    verrouillée » dit qu'il n'y a pas eu effraction. La vérification retirait « effraction = non » (« non dit ») et
    gardait « acces_voleur = sans_effraction » ; le vol restait incertain au lieu d'être refusé (f-d18, 7.94). Un
    fait déjà lu n'est jamais remplacé."""
    notes = []
    for v, regles in ((v, d.get("implique")) for v, d in voc.items() if d.get("implique")):
        valeurs = faits.get(v)
        for x in valeurs if isinstance(valeurs, list) else [valeurs]:
            for w, y in (regles.get(x) or {}).items():
                if w in voc and faits.get(w) in (None, "", []):
                    faits = faits | {w: [y] if voc[w].get("plusieurs") else y}
                    notes.append(f"{w} = {y} : dit par {v} = {x}")
                elif w in voc and voc[w].get("plusieurs") and y not in faits[w]:
                    # Une variable à plusieurs valeurs reçoit la valeur en plus : « les égouts ont refoulé »
                    # (`cause_eau = inondation`) est aussi une catastrophe naturelle, sans que l'eau soit retirée (7.105).
                    faits = faits | {w: [*faits[w], y]}
                    notes.append(f"{w} + {y} : dit par {v} = {x}")
    return faits, notes


def preciser(faits: dict, voc: dict) -> tuple[dict, list[str]]:
    """Une valeur vague remplacée par la précise quand un autre fait la désigne (vocabulaire, clé « preciser ») :
    un « accident » sur une vitre ou un miroir est un bris de vitrage (7.86). Le petit modèle lisait « accident »
    pour « j'ai cogné le miroir avec l'aspirateur », malgré l'aide ; chez l'assureur B, où la casse accidentelle
    n'est pas traduite, la réponse tombait à « incertain » au lieu de « couvert »."""
    notes = []
    for v, regles in ((v, d.get("preciser")) for v, d in voc.items() if d.get("preciser")):
        for vague, rs in regles.items():
            # Plusieurs règles possibles, dans l'ordre (7.97) ; « en » nul : la valeur vague est retirée, quand une
            # autre valeur lue dit déjà ce qui s'est passé (« accident » à côté de « tempête » ou de « responsabilité »).
            for r in rs if isinstance(rs, list) else [rs]:
                valeurs = faits.get(v)
                liste = valeurs if isinstance(valeurs, list) else [valeurs]
                if vague not in liste:
                    break
                if not any(set(r["si"].get(w, [])) & set(faits.get(w) if isinstance(faits.get(w), list) else [faits.get(w)])
                           for w in r["si"]):
                    continue
                if r.get("en") is None:
                    nouvelles = [e for e in liste if e != vague]
                    if not nouvelles:
                        continue
                    notes.append(f"{v} = {vague} retiré : {', '.join(nouvelles)} le dit déjà")
                else:
                    nouvelles = list(dict.fromkeys(r["en"] if e == vague else e for e in liste))
                    notes.append(f"{v} = {vague} précisé en {r['en']}")
                faits = faits | {v: nouvelles if isinstance(valeurs, list) else nouvelles[0]}
                break
    return faits, notes


def description_variable(v: str, d: dict) -> str:
    """Une ligne de vocabulaire pour le modèle : la question, les valeurs, le sens des valeurs proches."""
    aide = d.get("aide", {})
    valeurs = ", ".join(f"{x} ({aide[x]})" if x in aide else x for x in d["valeurs"])
    return f"- {v}{' (plusieurs)' if d.get('plusieurs') else ''} — {d.get('question', '')} : {valeurs}"


def question(variable: str) -> str:
    if variable == "lien_causal":
        return "Le non-respect de l'obligation de prévention a-t-il permis ou facilité le sinistre ?"
    return prolog.vocabulaire().get(variable, {}).get("question", f"Préciser : {variable}")
