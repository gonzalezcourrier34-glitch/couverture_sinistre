// # Présentation : libellés, couleurs, faits (sans Angular, testé avec vitest)

import {
    APreciser,
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
