import {
    Component,
    DestroyRef,
    OnInit,
    computed,
    inject,
    signal
} from '@angular/core';

import {
    takeUntilDestroyed
} from '@angular/core/rxjs-interop';

import {
    KeyValuePipe
} from '@angular/common';

import {
    HttpErrorResponse
} from '@angular/common/http';

import {
    APreciser,
    Citation,
    Clause,
    Contrat,
    Decision,
    Etape,
    Sante
} from './couverture.model';

import {
    CouvertureService
} from './couverture.service';

import {
    LIBELLES,
    TONS,
    fusionner,
    lignesDeFaits,
    lisible,
    pourcent,
    trierAPreciser
} from './presentation';


// # Constantes

/** Exemples de déclarations, proposés sous la saisie. */
const EXEMPLES = [
    'En faisant du vélo dans le parc, je n’ai pas vu un piéton et je l’ai renversé. Il s’est cassé le poignet.',
    'Le tuyau de ma machine à laver a éclaté : l’eau a traversé le plancher et abîmé le plafond du voisin du dessous.',
    'On a forcé la porte de ma cave et on m’a volé mon vélo.'
];

const LONGUEUR_MIN = 10;

const LONGUEUR_MAX = 2000;


// # Erreurs de l'API, en une phrase

function messageErreur(
    erreur: unknown
): string {
    if (erreur instanceof HttpErrorResponse) {
        if (erreur.status === 0) {
            return 'L’API ne répond pas : lancez `uv run couverture api` (port 8001).';
        }
        const detail = erreur.error?.detail;
        if (typeof detail === 'string') {
            return detail;
        }
        if (Array.isArray(detail) && detail.length) {
            return detail.map((d: { msg?: string }) => d.msg ?? '').join(' ; ');
        }
        if (erreur.status === 401 || erreur.status === 500) {
            return 'L’API refuse l’appel : vérifiez COUVERTURE_API_KEY dans le .env du projet, puis relancez npm start.';
        }
        return `Erreur ${erreur.status} de l’API.`;
    }
    return 'Erreur inattendue.';
}


// # Composant

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [KeyValuePipe],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {

    private readonly service = inject(CouvertureService);

    private readonly destroyRef = inject(DestroyRef);


    // # Aides au gabarit

    readonly exemples = EXEMPLES;

    readonly longueurMax = LONGUEUR_MAX;

    readonly libelles = LIBELLES;

    readonly tons = TONS;

    readonly lisible = lisible;

    readonly pourcent = pourcent;

    readonly lignesDeFaits = lignesDeFaits;


    // # État

    readonly sante = signal<Sante | null>(null);

    readonly santeErreur = signal<string | null>(null);

    readonly contrats = signal<Contrat[]>([]);

    readonly contratId = signal<string | null>(null);

    readonly sinistre = signal('');

    readonly chargement = signal(false);

    /** Ce qui est en cours, affiché pendant l'attente. */
    readonly attente = signal('');

    readonly erreur = signal<string | null>(null);

    /** L'échange en cours : la première analyse, puis chaque décision après des réponses. */
    readonly etapes = signal<Etape[]>([]);

    /** Réponses du client aux points à préciser de la dernière étape. */
    readonly reponses = signal<Record<string, string>>({});

    /** Clauses du contrat choisi, chargées à la première citation ouverte. */
    private readonly clausesParContrat = signal<Record<string, Record<string, Clause>>>({});

    /** Citations dont le texte complet est déplié (clé : étape-citation). */
    readonly ouvertes = signal<Set<string>>(new Set());


    // # Dérivés

    readonly decidables = computed(
        () => this.contrats().filter((c) => c.regles)
    );

    readonly contrat = computed(
        () => this.contrats().find((c) => c.id === this.contratId()) ?? null
    );

    readonly derniere = computed(() => {
        const etapes = this.etapes();
        return etapes.length ? etapes[etapes.length - 1] : null;
    });

    readonly aPreciser = computed<APreciser[]>(
        () => trierAPreciser(this.derniere()?.reponse.a_preciser ?? [])
    );

    readonly peutAnalyser = computed(() => {
        const longueur = this.sinistre().trim().length;
        return !!this.contratId() && longueur >= LONGUEUR_MIN && longueur <= LONGUEUR_MAX && !this.chargement();
    });

    readonly nbReponses = computed(
        () => Object.values(this.reponses()).filter((v) => !!v).length
    );


    // # Démarrage

    ngOnInit(): void {
        this.service.sante()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (sante) => this.sante.set(sante),
                error: (e) => this.santeErreur.set(messageErreur(e))
            });

        this.service.contrats()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (contrats) => {
                    this.contrats.set(contrats);
                    const premier = contrats.find((c) => c.regles);
                    if (premier && !this.contratId()) {
                        this.contratId.set(premier.id);
                    }
                },
                error: (e) => this.erreur.set(messageErreur(e))
            });
    }


    // # Saisie

    choisirContrat(
        id: string
    ): void {
        if (id === this.contratId()) {
            return;
        }
        this.contratId.set(id);
        this.nouvelleDeclaration(false);
    }

    saisir(
        evenement: Event
    ): void {
        this.sinistre.set((evenement.target as HTMLTextAreaElement).value);
    }

    exemple(
        texte: string
    ): void {
        this.sinistre.set(texte);
    }

    nouvelleDeclaration(
        viderTexte = true
    ): void {
        if (viderTexte) {
            this.sinistre.set('');
        }
        this.etapes.set([]);
        this.reponses.set({});
        this.ouvertes.set(new Set());
        this.erreur.set(null);
    }


    // # Analyse d'une déclaration (le modèle lit, le moteur décide)

    analyser(): void {
        const contratId = this.contratId();
        const sinistre = this.sinistre().trim();
        if (!contratId || !this.peutAnalyser()) {
            return;
        }
        this.lancer('Le modèle lit la déclaration, le moteur décide…');
        this.service.analyser(contratId, sinistre)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (reponse) => this.ajouter({ origine: 'analyse', texte: sinistre, reponse }, true),
                error: (e) => this.echec(e)
            });
    }


    // # Réponses du client (le moteur seul, sans modèle)

    repondre(
        variable: string,
        valeur: string
    ): void {
        this.reponses.update((r) => ({ ...r, [variable]: r[variable] === valeur ? '' : valeur }));
    }

    decider(): void {
        const contratId = this.contratId();
        const derniere = this.derniere();
        if (!contratId || !derniere || !this.nbReponses() || this.chargement()) {
            return;
        }
        const reponses = this.reponses();
        const resume = Object.entries(reponses)
            .filter(([, v]) => !!v)
            .map(([variable, valeur]) => `${lisible(variable)} : ${lisible(valeur)}`)
            .join(' ; ');
        this.lancer('Le moteur décide…');
        this.service.decider(contratId, fusionner(derniere.reponse.faits, reponses))
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (reponse) => this.ajouter({ origine: 'reponses', texte: resume, reponse }, false),
                error: (e) => this.echec(e)
            });
    }


    // # Citations : le texte complet de la clause

    cle(
        indexEtape: number,
        citation: Citation
    ): string {
        return `${indexEtape}:${citation.clause_id}:${citation.extrait.slice(0, 40)}`;
    }

    estOuverte(
        cle: string
    ): boolean {
        return this.ouvertes().has(cle);
    }

    basculer(
        cle: string
    ): void {
        const contratId = this.contratId();
        this.ouvertes.update((o) => {
            const copie = new Set(o);
            if (copie.has(cle)) {
                copie.delete(cle);
            } else {
                copie.add(cle);
            }
            return copie;
        });
        if (contratId && !this.clausesParContrat()[contratId]) {
            this.service.clauses(contratId)
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({
                    next: (clauses) => this.clausesParContrat.update((c) => ({
                        ...c,
                        [contratId]: Object.fromEntries(clauses.map((x) => [x.id, x]))
                    })),
                    error: (e) => this.erreur.set(messageErreur(e))
                });
        }
    }

    clause(
        clauseId: string
    ): Clause | null {
        const contratId = this.contratId();
        return contratId ? this.clausesParContrat()[contratId]?.[clauseId] ?? null : null;
    }


    // # Interne

    private lancer(
        texte: string
    ): void {
        this.attente.set(texte);
        this.chargement.set(true);
        this.erreur.set(null);
    }

    private ajouter(
        etape: Etape,
        nouvelle: boolean
    ): void {
        this.etapes.update((etapes) => (nouvelle ? [etape] : [...etapes, etape]));
        this.reponses.set({});
        if (nouvelle) {
            this.ouvertes.set(new Set());
        }
        this.chargement.set(false);
    }

    private echec(
        erreur: unknown
    ): void {
        this.erreur.set(messageErreur(erreur));
        this.chargement.set(false);
    }
}
