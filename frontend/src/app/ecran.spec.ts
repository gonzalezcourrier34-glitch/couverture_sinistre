// # L'écran découpé en composants (13.1) : l'état commun et l'affichage d'une étape, sans API (vitest, jsdom)

import { describe, expect, it, beforeEach } from 'vitest';

import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { EtapeComponent } from './composants/etape.component';
import { APreciser, Decision, Etape, Sinistre } from './couverture.model';
import { EchangeService } from './echange.service';


function decision(partiel: Partial<Decision> = {}): Decision {
    return {
        contrat_id: 'c1', decision: 'INCERTAIN', justification: 'À préciser.', confiance: 0.5, a_preciser: [],
        questions: [], citations: [], limites: [], faits: {}, faits_affiches: [], avertissements: [],
        raisonnement: [], mode: 'clauses', durees_ms: {}, chapitres: [], sinistres: [], ...partiel
    };
}

const SERRURE: APreciser = {
    variable: 'fermeture', nature: 'question', question: 'Comment le local était-il fermé ?',
    valeurs: ['serrure', 'cadenas'], libelles: { serrure: 'serrure', cadenas: 'cadenas' }, aide: {}
};


describe('l’état de l’échange', () => {
    let ech: EchangeService;

    beforeEach(() => {
        TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
        ech = TestBed.inject(EchangeService);
    });

    it('pose une question une seule fois, avec ses réponses proposées, puis les questions en phrase', () => {
        const reponse = decision({
            a_preciser: [SERRURE],
            questions: ['Comment le local était-il fermé ? (serrure → couvert)', 'Le vol est-il lié à l’effraction ?']
        });
        ech.etapes.set([{ origine: 'analyse', texte: 'On a volé mon vélo dans la cave.', reponse }]);
        expect(ech.enMots()).toBe(true);
        expect(ech.questionsEnMots()).toEqual([
            { texte: 'Comment le local était-il fermé ?', valeurs: ['serrure', 'cadenas'] },
            { texte: 'Le vol est-il lié à l’effraction ?', valeurs: [] }
        ]);
    });

    it('répond en mots pour plusieurs sinistres, même avec la chaîne de règles', () => {
        const sinistre = (titre: string): Sinistre => ({ ...decision({ mode: 'regles:test' }), titre, declaration: titre });
        ech.etapes.set([{ origine: 'analyse', texte: 'Deux sinistres.',
            reponse: decision({ mode: 'regles:test', sinistres: [sinistre('Le vol'), sinistre('Le gel')] }) }]);
        expect(ech.enMots()).toBe(true);
        ech.etapes.set([{ origine: 'analyse', texte: 'Un sinistre.', reponse: decision({ mode: 'regles:test' }) }]);
        expect(ech.enMots()).toBe(false);
    });
});


describe('répondre aux questions des règles par le moteur seul (13.4)', () => {
    it('quand la lecture des clauses attend seulement les règles, et qu’elles ont lu les faits', () => {
        TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
        const ech = TestBed.inject(EchangeService);
        const reponse = decision({ a_preciser: [SERRURE], questions: ['Comment le local était-il fermé ?'],
            faits: { evenement: ['vol'], bien: ['velo'], lieu: ['cave'] } });
        ech.etapes.set([{ origine: 'analyse', texte: 'On a volé mon vélo dans la cave.', reponse }]);
        expect(ech.parMoteur()).toBe(true);
        expect(ech.enMots()).toBe(false);
        ech.etapes.set([{ origine: 'analyse', texte: 'Idem.', reponse: { ...reponse, questions: [...reponse.questions, 'La formule Confort ?'] } }]);
        expect(ech.parMoteur()).toBe(false);
    });
});


describe('une étape à l’écran', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    });

    it('montre une décision par sinistre', async () => {
        const vol: Sinistre = { ...decision({ decision: 'INCERTAIN' }), titre: 'Le vol', declaration: 'vol' };
        const gel: Sinistre = { ...decision({ decision: 'COUVERT', justification: 'Couvert.' }), titre: 'Le gel', declaration: 'gel' };
        const etape: Etape = { origine: 'analyse', texte: 'Deux sinistres.', reponse: decision({ sinistres: [vol, gel] }) };
        const fixture = TestBed.createComponent(EtapeComponent);
        fixture.componentRef.setInput('courante', etape);
        fixture.componentRef.setInput('derniere', true);
        fixture.detectChanges();
        await fixture.whenStable();
        const page: HTMLElement = fixture.nativeElement;
        expect(Array.from(page.querySelectorAll('.sinistre-titre')).map((e) => e.textContent?.trim())).toEqual(['1. Le vol', '2. Le gel']);
        expect(Array.from(page.querySelectorAll('.verdict-libelle')).map((e) => e.textContent?.trim())).toEqual(['À préciser', 'Couvert']);
    });
});
