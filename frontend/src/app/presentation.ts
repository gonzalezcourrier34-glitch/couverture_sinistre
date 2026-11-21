// # Présentation : libellés, couleurs, faits (sans Angular, testé avec vitest)

import {
    APreciser,
    Citation,
    DecisionValeur,
    Faits
} from './couverture.model';


export const LIBELLES: Record<DecisionValeur, string> = {
    COUVERT: 'Couvert',
    NON_COUVERT: 'Non couvert',
    INCERTAIN: 'À préciser'
};

/** Classe CSS de la décision (couleurs du système de design : succès, danger, avertissement). */
export const TONS: Record<DecisionValeur, string> = {
    COUVERT: 'ton-succes',
    NON_COUVERT: 'ton-danger',
    INCERTAIN: 'ton-attention'
};


/** `origine_rc` → « origine rc » ; `animal_compagnie` → « animal compagnie ». */
export function lisible(
    identifiant: string
): string {
    return identifiant.replace(/_/g, ' ');
}


/** Les faits en lignes « variable : valeur(s) », le socle (événement, bien, lieu) d'abord. */
export function lignesDeFaits(
    faits: Faits
): { variable: string; valeur: string }[] {
    const ordre = ['evenement', 'bien', 'lieu'];
    const variables = Object.keys(faits).sort(
        (a, b) => (ordre.indexOf(a) + 1 || 99) - (ordre.indexOf(b) + 1 || 99) || a.localeCompare(b)
    );
    return variables.map((variable) => {
        const valeur = faits[variable];
        return {
            variable: lisible(variable),
            valeur: (Array.isArray(valeur) ? valeur : [valeur]).map(lisible).join(', ')
        };
    });
}


/** Les faits d'une réponse, complétés par les réponses du client (une réponse vide est ignorée). */
export function fusionner(
    faits: Faits,
    reponses: Record<string, string>
): Faits {
    const complets: Faits = { ...faits };
    for (const [variable, valeur] of Object.entries(reponses)) {
        if (valeur) {
            complets[variable] = valeur;
        }
    }
    return complets;
}


/** Les questions d'abord (sans elles, pas de décision), puis les réserves. */
export function trierAPreciser(
    points: APreciser[]
): APreciser[] {
    return [...points].sort((a, b) => Number(a.nature === 'reserve') - Number(b.nature === 'reserve'));
}


/** Pourcentage de confiance, arrondi. */
export function pourcent(
    confiance: number
): string {
    return `${Math.round(confiance * 100)} %`;
}


// # Clauses citées

/** Un article cité, avec tous les extraits que la décision en tire. */
export interface ArticleCite {
    clauseId: string;
    role: string;
    pages: number[];
    extraits: string[];
}

/** Les citations regroupées par article, dans l'ordre de la décision : un article, une ligne, ses extraits. */
export function citationsParArticle(
    citations: Citation[]
): ArticleCite[] {
    const articles = new Map<string, ArticleCite>();
    for (const citation of citations) {
        let article = articles.get(citation.clause_id);
        if (!article) {
            article = { clauseId: citation.clause_id, role: citation.role, pages: [...citation.pages], extraits: [] };
            articles.set(citation.clause_id, article);
        }
        if (!article.extraits.includes(citation.extrait)) {
            article.extraits.push(citation.extrait);
        }
    }
    return [...articles.values()];
}

/** Le texte d'un article découpé en morceaux, ceux qui sont cités marqués : pour les surligner à la lecture. */
export function surligner(
    texte: string,
    extraits: string[]
): { texte: string; cite: boolean }[] {
    const plages: [number, number][] = [];
    for (const extrait of extraits) {
        const debut = extrait ? texte.indexOf(extrait) : -1;
        if (debut !== -1) {
            plages.push([debut, debut + extrait.length]);
        }
    }
    plages.sort((a, b) => a[0] - b[0]);
    const morceaux: { texte: string; cite: boolean }[] = [];
    let position = 0;
    for (const [debut, fin] of plages) {
        if (fin <= position) {
            continue;
        }
        if (debut > position) {
            morceaux.push({ texte: texte.slice(position, debut), cite: false });
        }
        morceaux.push({ texte: texte.slice(Math.max(debut, position), fin), cite: true });
        position = fin;
    }
    if (position < texte.length) {
        morceaux.push({ texte: texte.slice(position), cite: false });
    }
    return morceaux;
}
