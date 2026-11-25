// # Types échangés avec l'API (`src/couverture/api/schemas.py`)

export type DecisionValeur = 'COUVERT' | 'NON_COUVERT' | 'INCERTAIN';

export type Faits = Record<string, string | string[]>;

export interface Sante {
    statut: 'ok' | 'degrade';
    version: string;
    contrats_decidables: string[];
    prolog: boolean;
    modele: string | null;
    cle_api_configuree: boolean;
}

export interface Contrat {
    id: string;
    assureur: string;
    produit: string;
    version: string;
    statut: string;
    nb_clauses: number | null;
    alertes: string[];
    regles: boolean;
    /** Les conditions générales sont-elles traduites en règles en entier ? Et le détail, en une phrase. */
    complet?: boolean;
    traduction?: string;
    /** Ce que les conditions particulières du client peuvent préciser : la formule, les options. */
    souscription?: Souscription[];
}

/** Un point des conditions particulières (« Formule », « Garantie vol souscrite ») et ses valeurs possibles. */
export interface Souscription {
    variable: string;
    libelle: string;
    question: string;
    valeurs: string[];
    libelles: Record<string, string>;
}

export interface Clause {
    id: string;
    article: string;
    titre: string;
    chemin: string[];
    type: string;
    texte: string;
    pages: number[];
    renvois: string[];
}

export interface APreciser {
    variable: string;
    nature: 'question' | 'reserve';
    question: string;
    valeurs: string[];
    /** Le texte à montrer pour chaque valeur (« voie_publique » → « voie publique »). */
    libelles?: Record<string, string>;
    aide: Record<string, string>;
}

/** Un fait tel qu'on le montre : « Lieu : voie publique ». */
export interface FaitAffiche {
    variable: string;
    libelle: string;
    valeur: string;
}

export interface Citation {
    clause_id: string;
    extrait: string;
    role: string;
    valide: boolean;
    pages: number[];
}

export interface Limite {
    clause_id: string;
    extrait: string;
    montant: string;
}

export interface Decision {
    contrat_id: string | null;
    decision: DecisionValeur;
    justification: string;
    confiance: number;
    a_preciser: APreciser[];
    questions: string[];
    citations: Citation[];
    limites: Limite[];
    faits: Faits;
    faits_affiches?: FaitAffiche[];
    avertissements: string[];
    raisonnement: string[];
    mode: string;
    durees_ms: Record<string, number>;
}

/** Une étape de l'échange : une analyse de déclaration, ou une décision après les réponses du client. */
export interface Etape {
    origine: 'analyse' | 'reponses';
    texte: string;
    reponse: Decision;
}

/** Un message du suivi d'une analyse : une étape qui commence (sans détail), qui finit (avec), la fin, ou une erreur. */
export interface Suivi {
    etape?: string;
    detail?: string;
    reponse?: Decision;
    code?: number;
    /** En premier, avec la lecture clause par clause : ses étapes, et ce qu'il faut savoir avant d'attendre. */
    etapes?: EtapeSuivi[];
    annonce?: string;
}

/** Une étape annoncée de l'analyse : sa clé dans le suivi, et ce qu'on en dit à l'écran. */
export interface EtapeSuivi {
    cle: string;
    titre: string;
}
