import { describe, expect, it } from 'vitest';

import { fusionner, lignesDeFaits, lisible, pourcent, trierAPreciser } from './presentation';


describe('présentation des décisions', () => {
    it('rend les identifiants lisibles', () => {
        expect(lisible('animal_compagnie')).toBe('animal compagnie');
    });

    it('met le socle en tête des faits', () => {
        const lignes = lignesDeFaits({ victime: 'tiers', lieu: ['cave'], evenement: ['vol'], bien: ['velo'] });
        expect(lignes.map((l) => l.variable)).toEqual(['evenement', 'bien', 'lieu', 'victime']);
    });

    it('ajoute les réponses du client aux faits, sans les vides', () => {
        const faits = fusionner({ evenement: ['vol'], fermeture: 'aucune' }, { fermeture: 'cadenas', effraction: '' });
        expect(faits).toEqual({ evenement: ['vol'], fermeture: 'cadenas' });
    });

    it('place les questions avant les réserves', () => {
        const tries = trierAPreciser([
            { variable: 'option', nature: 'reserve', question: '?', valeurs: [], aide: {} },
            { variable: 'fermeture', nature: 'question', question: '?', valeurs: [], aide: {} }
        ]);
        expect(tries[0].variable).toBe('fermeture');
    });

    it('arrondit la confiance', () => {
        expect(pourcent(0.854)).toBe('85 %');
    });
});
