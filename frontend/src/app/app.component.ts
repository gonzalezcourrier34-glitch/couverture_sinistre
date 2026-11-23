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
    citationsParArticle,
    fusionner,
    lignesDeFaits,
    lisible,
    pourcent,
    surligner,
    trierAPreciser
} from './presentation';


// # Constantes

/** Exemples de déclarations, proposés sous la saisie : un titre court sur le bouton, le texte dans la zone de saisie. */
const EXEMPLES: readonly { titre: string; texte: string }[] = [
    {
        titre: 'Piéton renversé à vélo',
        texte: 'En faisant du vélo dans le parc, je n’ai pas vu un piéton et je l’ai renversé. Il s’est cassé le poignet.'
    },
    {
        titre: 'Fuite de machine à laver',
        texte: 'Le tuyau de ma machine à laver a éclaté : l’eau a traversé le plancher et abîmé le plafond du voisin du dessous.'
    },
    {
        titre: 'Vélo volé dans la cave',
        texte: 'On a forcé la porte de ma cave et on m’a volé mon vélo.'
    }
];

/** Les étapes d'une analyse, dans l'ordre où l'API les annonce (`POST /analyses/suivi`). */
const ETAPES_SUIVI: readonly { cle: string; titre: string }[] = [
    { cle: 'socle', titre: 'Lire ce qui s’est passé, ce qui est touché, et où' },
    { cle: 'details', titre: 'Lire les détails qui comptent pour cet événement' },
    { cle: 'verification', titre: 'Vérifier que chaque fait est dans la déclaration' },
    { cle: 'decision', titre: 'Appliquer les règles du contrat' },
    { cle: 'confirmation', titre: 'Confirmer les faits qui portent la réponse' }
];

/** Le temps de lire la dernière ligne du suivi avant que la fenêtre se referme (ms). */
const PAUSE_FIN_SUIVI = 1200;

/** Au-delà, les réponses possibles à une question s'affichent en liste déroulante, plus en boutons. */
const MAX_PUCES = 10;

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
    imports: [KeyValuePipe],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss',
    host: {
        '(document:keydown.escape)': 'fermerArticle()'
    }
})
export class AppComponent implements OnInit {

    private readonly service = inject(CouvertureService);

    private readonly destroyRef = inject(DestroyRef);


    // # Aides au gabarit

    readonly exemples = EXEMPLES;

    readonly longueurMax = LONGUEUR_MAX;

    readonly maxPuces = MAX_PUCES;

    readonly etapesSuivi = ETAPES_SUIVI;

    readonly libelles = LIBELLES;

    readonly tons = TONS;

    readonly lisible = lisible;

    readonly pourcent = pourcent;

    readonly lignesDeFaits = lignesDeFaits;

    readonly citationsParArticle = citationsParArticle;

    readonly surligner = surligner;


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

    /** Clauses du contrat choisi, chargées au premier article ouvert. */
    private readonly clausesParContrat = signal<Record<string, Record<string, Clause>>>({});

    /** La fenêtre de suivi de l'analyse est affichée. */
    readonly suiviOuvert = signal(false);

    /** Où en est chaque étape de l'analyse en cours, et ce qu'elle a donné. */
    readonly suivi = signal<Record<string, { etat: 'encours' | 'fait'; detail?: string }>>({});

    /** Une fiche PDF est en cours de production. */
    readonly ficheEnCours = signal(false);

    /** L'article affiché en entier dans la fenêtre, avec les extraits à y surligner. */
    readonly articleOuvert = signal<{ clauseId: string; extraits: string[] } | null>(null);


    // # Dérivés

    readonly decidables = computed(
        () => this.contrats().filter((c) => c.regles)
    );

    readonly contrat = computed(
        () => this.contrats().find((c) => c.id === this.contratId()) ?? null
    );

    /** Ce que les conditions particulières du client disent (la formule, les options) ; vide : non renseigné. */
    readonly souscription = signal<Record<string, string>>({});

    readonly nbSouscription = computed(
        () => Object.values(this.souscription()).filter((v) => !!v).length
    );

    readonly derniere = computed(() => {
        const etapes = this.etapes();
        return etapes.length ? etapes[etapes.length - 1] : null;
    });

    readonly aPreciser = computed<APreciser[]>(
        () => trierAPreciser(this.derniere()?.reponse.a_preciser ?? [])
    );

    /** Sans la réponse, pas de décision : ce sont les seules questions posées au client. */
    readonly questions = computed<APreciser[]>(
        () => this.aPreciser().filter((p) => p.nature === 'question')
    );

    /** La réponse est « couvert » ; l'assureur pourra vérifier ces points : affichés, pas demandés. */
    readonly reserves = computed<APreciser[]>(
        () => this.aPreciser().filter((p) => p.nature === 'reserve')
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
        this.souscription.set({});
        this.nouvelleDeclaration(false);
    }

    /** Renseigne un point des conditions particulières ; la valeur vide le remet à « non renseigné ». */
    souscrire(
        variable: string,
        evenement: Event
    ): void {
        const valeur = (evenement.target as HTMLSelectElement).value;
        this.souscription.update((s) => ({ ...s, [variable]: valeur }));
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
            // Une nouvelle déclaration est celle d'un autre client : ses conditions particulières ne sont pas les mêmes.
            this.sinistre.set('');
            this.souscription.set({});
        }
        this.etapes.set([]);
        this.reponses.set({});
        this.articleOuvert.set(null);
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
        this.suivi.set({});
        this.suiviOuvert.set(true);
        const souscription = Object.fromEntries(Object.entries(this.souscription()).filter(([, v]) => !!v));
        this.service.analyserAvecSuivi(contratId, sinistre, souscription)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (message) => {
                    if (message.etape === 'fin' && message.reponse) {
                        const reponse = message.reponse;
                        setTimeout(() => {
                            this.suiviOuvert.set(false);
                            this.ajouter({ origine: 'analyse', texte: sinistre, reponse }, true);
                        }, PAUSE_FIN_SUIVI);
                    } else if (message.etape === 'erreur') {
                        this.suiviOuvert.set(false);
                        this.erreur.set(message.detail ?? 'L’analyse a échoué.');
                        this.chargement.set(false);
                    } else {
                        this.suivi.update((s) => ({
                            ...s,
                            [message.etape]: message.detail === undefined
                                ? { etat: 'encours' }
                                : { etat: 'fait', detail: message.detail }
                        }));
                    }
                },
                error: (e) => {
                    this.suiviOuvert.set(false);
                    this.echec(e);
                }
            });
    }


    // # Réponses du client (le moteur seul, sans modèle)

    repondre(
        variable: string,
        valeur: string
    ): void {
        this.reponses.update((r) => ({ ...r, [variable]: r[variable] === valeur ? '' : valeur }));
    }

    /** La réponse choisie dans une liste déroulante (vide : aucune). */
    choisir(
        variable: string,
        evenement: Event
    ): void {
        const valeur = (evenement.target as HTMLSelectElement).value;
        this.reponses.update((r) => ({ ...r, [variable]: valeur }));
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
            .map(([variable, valeur]) => {
                const point = derniere.reponse.a_preciser.find((p) => p.variable === variable);
                return `${point?.question ?? lisible(variable)} ${point?.libelles?.[valeur] ?? lisible(valeur)}`;
            })
            .join(' ; ');
        this.lancer('Le moteur décide…');
        this.service.decider(contratId, fusionner(derniere.reponse.faits, reponses))
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (reponse) => this.ajouter({ origine: 'reponses', texte: resume, reponse }, false),
                error: (e) => this.echec(e)
            });
    }


    // # Clauses citées : l'article entier, dans une fenêtre

    ouvrirArticle(
        clauseId: string,
        extraits: string[]
    ): void {
        const contratId = this.contratId();
        this.articleOuvert.set({ clauseId, extraits });
        // Seule la clause ouverte est demandée : en ligne, le contrat entier ne se télécharge pas.
        if (contratId && !this.clausesParContrat()[contratId]?.[clauseId]) {
            this.service.clause(contratId, clauseId)
                .pipe(takeUntilDestroyed(this.destroyRef))
                .subscribe({
                    next: (clause) => this.clausesParContrat.update((c) => ({
                        ...c,
                        [contratId]: { ...(c[contratId] ?? {}), [clause.id]: clause }
                    })),
                    error: (e) => {
                        this.articleOuvert.set(null);
                        this.erreur.set(messageErreur(e));
                    }
                });
        }
    }

    fermerArticle(): void {
        this.articleOuvert.set(null);
    }

    clause(
        clauseId: string
    ): Clause | null {
        const contratId = this.contratId();
        return contratId ? this.clausesParContrat()[contratId]?.[clauseId] ?? null : null;
    }


    // # La fiche de la décision, en PDF

    telechargerFiche(
        etape: Etape
    ): void {
        const contratId = this.contratId();
        const declaration = this.etapes()[0]?.texte ?? etape.texte;
        if (!contratId || this.ficheEnCours()) {
            return;
        }
        const sinistre = etape.origine === 'reponses'
            ? `${declaration}\nRéponses du client : ${etape.texte}`
            : declaration;
        this.ficheEnCours.set(true);
        this.service.fiche(contratId, sinistre.slice(0, 4000), etape.reponse)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: (pdf) => {
                    const adresse = URL.createObjectURL(pdf);
                    const lien = document.createElement('a');
                    lien.href = adresse;
                    lien.download = `fiche-sinistre-${contratId}.pdf`;
                    lien.click();
                    URL.revokeObjectURL(adresse);
                    this.ficheEnCours.set(false);
                },
                error: (e) => {
                    this.erreur.set(messageErreur(e));
                    this.ficheEnCours.set(false);
                }
            });
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
        this.chargement.set(false);
    }

    private echec(
        erreur: unknown
    ): void {
        this.erreur.set(messageErreur(erreur));
        this.chargement.set(false);
    }
}
