import { describe, expect, it } from 'vitest';

import { citationsParArticle, fusionner, lignesDeFaits, lisible, pourcent, surligner, trierAPreciser } from './presentation';


describe('présentation des décisions', () => {
    it('rend les identifiants lisibles', () => {
        expect(lisible('animal_compagnie')).toBe('animal compagnie');
    });

    it('met le socle en tête des faits', () => {
        const lignes = lignesDeFaits({ victime: 'tiers', lieu: ['cave'], evenement: ['vol'], bien: ['velo'] });
        expect(lignes.map((l) => l.variable)).toEqual(['evenement', 'bien', 'lieu', 'victime']);
    });

    it('montre les libellés du vocabulaire quand l’API les donne', () => {
        const lignes = lignesDeFaits({ lieu: ['voie_publique'] }, [{ variable: 'lieu', libelle: 'Lieu', valeur: 'voie publique' }]);
        expect(lignes).toEqual([{ variable: 'Lieu', valeur: 'voie publique' }]);
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

    it('regroupe les citations par article, sans répéter un extrait', () => {
        const citation = (clause_id: string, extrait: string) => ({ clause_id, extrait, role: 'garantie', valide: true, pages: [11] });
        const articles = citationsParArticle([citation('2.10', 'a'), citation('12/vol', 'b'), citation('2.10', 'c'), citation('2.10', 'a')]);
        expect(articles.map((a) => a.clauseId)).toEqual(['2.10', '12/vol']);
        expect(articles[0].extraits).toEqual(['a', 'c']);
    });

    it('surligne les extraits cités dans le texte de l’article', () => {
        expect(surligner('Le vol du contenu, sauf la disparition.', ['vol du contenu', 'absent'])).toEqual([
            { texte: 'Le ', cite: false },
            { texte: 'vol du contenu', cite: true },
            { texte: ', sauf la disparition.', cite: false }
        ]);
        expect(surligner('abc', [])).toEqual([{ texte: 'abc', cite: false }]);
    });
});
