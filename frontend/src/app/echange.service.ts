import {
    Injectable,
    computed,
    inject,
    signal
} from '@angular/core';

import {
    HttpErrorResponse
} from '@angular/common/http';

import {
    APreciser,
    Clause,
    Contrat,
    Decision,
    Etape,
    EtapeSuivi,
    Methode,
    Sante
} from './couverture.model';

import {
    CouvertureService
} from './couverture.service';

import {
    fusionner,
    lisible,
    trierAPreciser
} from './presentation';


/*
 * L'échange en cours, et tout ce qu'on en fait (13.1) : le contrat choisi, la déclaration, les étapes (la première
 * analyse, puis chaque décision après des réponses), les réponses du client, le suivi de l'analyse, l'article ouvert,
 * la fiche. Un seul état pour l'écran : les composants le lisent et appellent ses méthodes ; aucun ne garde le sien.
 * Les requêtes HTTP se terminent d'elles-mêmes : pas d'abonnement à défaire.
 */

// # Constantes

/** Exemples de déclarations, proposés sous la saisie : un titre court sur le bouton, le texte dans la zone de saisie. */
export const EXEMPLES: readonly { titre: string; texte: string }[] = [
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
const ETAPES_SUIVI: readonly EtapeSuivi[] = [
    { cle: 'socle', titre: 'Lire ce qui s’est passé, ce qui est touché, et où' },
    { cle: 'details', titre: 'Lire les détails qui comptent pour cet événement' },
    { cle: 'verification', titre: 'Vérifier que chaque fait est dans la déclaration' },
    { cle: 'decision', titre: 'Appliquer les règles du contrat' },
    { cle: 'confirmation', titre: 'Confirmer les faits qui portent la réponse' }
];

/** Le temps de lire la dernière ligne du suivi avant que la fenêtre se referme (ms). */
const PAUSE_FIN_SUIVI = 1200;

/** Au-delà, les réponses possibles à une question s'affichent en liste déroulante, plus en boutons. */
export const MAX_PUCES = 10;

export const LONGUEUR_MIN = 10;

export const LONGUEUR_MAX = 2000;


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


// # L'échange

@Injectable({ providedIn: 'root' })
export class EchangeService {

    private readonly api = inject(CouvertureService);

    /** Les étapes affichées pendant l'analyse : celles de la chaîne de règles, sauf si l'API en annonce d'autres. */
    readonly etapesSuivi = signal<readonly EtapeSuivi[]>(ETAPES_SUIVI);

    /** Ce que l'API dit avant l'attente (la lecture clause par clause prend deux à trois minutes). */
    readonly annonceSuivi = signal<string | null>(null);


    // # État

    readonly sante = signal<Sante | null>(null);

    readonly santeErreur = signal<string | null>(null);

    /** La méthode de la prochaine analyse, choisie à l'écran : la lecture des clauses par défaut (7.216). */
    readonly methode = signal<Methode>('clauses');

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

    /** Lecture des clauses : les réponses du client aux questions de la dernière étape, en mots, par question (7.218). */
    readonly reponsesLibres = signal<Record<number, string>>({});

    /** La déclaration telle qu'elle a été envoyée en dernier : la base d'une nouvelle lecture après les réponses. */
    private readonly declarationEnvoyee = signal('');

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

    /**
     * Lecture des clauses, un seul sinistre, et toutes les questions sont celles des règles, avec les faits qu'elles
     * ont lus : le moteur décide seul avec les réponses, sans relire la déclaration (13.4).
     */
    readonly parMoteur = computed(() => {
        const r = this.derniere()?.reponse;
        if (!r || r.mode !== 'clauses' || this.plusieurs(r) || !Object.keys(r.faits ?? {}).length) {
            return false;
        }
        const points = r.a_preciser.filter((p) => p.nature === 'question').map((p) => p.question);
        return points.length > 0 && r.questions.every((q) => points.some((p) => q.startsWith(p)));
    });

    /**
     * On répond en mots, et la déclaration complétée est relue (7.218, 7.222) : avec la lecture des clauses (sauf
     * quand le moteur peut décider seul), et pour toute déclaration à plusieurs sinistres, quelle que soit la
     * méthode. Sinon le moteur décide seul.
     */
    readonly enMots = computed(() => {
        const r = this.derniere()?.reponse;
        return !!r && ((r.mode === 'clauses' && !this.parMoteur()) || this.plusieurs(r));
    });

    /**
     * Les questions auxquelles on répond en mots : celles qui ont des réponses proposées (les règles), puis celles
     * en phrase qu'elles ne disent pas déjà. Une même question n'est posée qu'une fois.
     */
    readonly questionsEnMots = computed<{ texte: string; valeurs: string[] }[]>(() => {
        const r = this.derniere()?.reponse;
        if (!r) {
            return [];
        }
        const points = r.a_preciser
            .filter((p) => p.nature === 'question')
            .map((p) => ({ texte: p.question, valeurs: p.valeurs.map((v) => p.libelles?.[v] ?? lisible(v)) }))
            .map((q) => (q.valeurs.length > MAX_PUCES ? { ...q, valeurs: [] } : q));
        const phrases = r.questions
            .filter((q) => !points.some((p) => q.startsWith(p.texte)))
            .map((q) => ({ texte: q, valeurs: [] as string[] }));
        return [...points, ...phrases];
    });

    readonly peutAnalyser = computed(() => {
        const longueur = this.sinistre().trim().length;
        return !!this.contratId() && longueur >= LONGUEUR_MIN && longueur <= LONGUEUR_MAX && !this.chargement();
    });

    readonly nbReponses = computed(
        () => Object.values(this.reponses()).filter((v) => !!v).length
    );

    readonly nbReponsesLibres = computed(
        () => Object.values(this.reponsesLibres()).filter((v) => !!v.trim()).length
    );

    /** La déclaration suivie des réponses du client : ce que relira la lecture des clauses. */
    readonly declarationAvecReponses = computed(() => {
        const questions = this.questionsEnMots().map((q) => q.texte);
        const lignes = questions
            .map((q, i) => ({ q, r: (this.reponsesLibres()[i] ?? '').trim() }))
            .filter((x) => !!x.r)
            .map((x) => `- ${x.q} ${x.r}`);
        return lignes.length ? `${this.declarationEnvoyee()}\n\nPrécisions du client :\n${lignes.join('\n')}` : '';
    });

    readonly reponsesTropLongues = computed(() => this.declarationAvecReponses().length > LONGUEUR_MAX);


    // # Démarrage

    /** Au démarrage de l'écran : l'état du service, et les contrats (le premier décidable est choisi). */
    demarrer(): void {
        this.api.sante()
            .subscribe({
                next: (sante) => this.sante.set(sante),
                error: (e) => this.santeErreur.set(messageErreur(e))
            });

        this.api.contrats()
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


    // # Le choix de la méthode

    choisirMethode(event: Event): void {
        const valeur = (event.target as HTMLSelectElement).value;
        this.methode.set(valeur === 'regles' ? 'regles' : 'clauses');
    }


    // # Analyse d'une déclaration (le modèle lit, le moteur décide)

    analyser(): void {
        if (!this.peutAnalyser()) {
            return;
        }
        this.analyserTexte(this.sinistre().trim(), this.methode(), null);
    }

    /**
     * Une analyse de `sinistre` par `methode`. `apresReponses` : le résumé des réponses du client quand c'est une
     * nouvelle lecture après ses réponses (7.218) ; l'étape s'ajoute alors à l'échange au lieu de le recommencer.
     */
    private analyserTexte(
        sinistre: string,
        methode: Methode,
        apresReponses: string | null,
        chapitres?: string[],
        lecture?: string
    ): void {
        const contratId = this.contratId();
        if (!contratId || this.chargement()) {
            return;
        }
        this.lancer(methode === 'clauses'
            ? 'Le modèle juge chaque clause, la logique tranche…'
            : 'Le modèle lit la déclaration, le moteur décide…');
        this.suivi.set({});
        this.etapesSuivi.set(ETAPES_SUIVI);
        this.annonceSuivi.set(null);
        this.suiviOuvert.set(true);
        const souscription = Object.fromEntries(Object.entries(this.souscription()).filter(([, v]) => !!v));
        this.api.analyserAvecSuivi(contratId, sinistre, souscription, methode, chapitres, lecture)
            .subscribe({
                next: (message) => {
                    if (message.etapes) {
                        this.etapesSuivi.set(message.etapes);
                        this.annonceSuivi.set(message.annonce ?? null);
                    } else if (message.etape === 'fin' && message.reponse) {
                        const reponse = message.reponse;
                        setTimeout(() => {
                            this.suiviOuvert.set(false);
                            this.declarationEnvoyee.set(sinistre);
                            this.ajouter(apresReponses === null
                                ? { origine: 'analyse', texte: sinistre, reponse }
                                : { origine: 'reponses', texte: apresReponses, reponse }, apresReponses === null);
                        }, PAUSE_FIN_SUIVI);
                    } else if (message.etape === 'erreur') {
                        this.suiviOuvert.set(false);
                        this.erreur.set(message.detail ?? 'L’analyse a échoué.');
                        this.chargement.set(false);
                    } else if (message.etape) {
                        const cle = message.etape;
                        this.suivi.update((s) => ({
                            ...s,
                            [cle]: message.detail === undefined
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


    // # Réponses du client, lecture des clauses : une nouvelle lecture, la déclaration complétée (7.218)

    repondreLibrement(
        index: number,
        valeur: string
    ): void {
        this.reponsesLibres.update((r) => ({ ...r, [index]: valeur }));
    }

    /** Le texte saisi dans le champ de réponse d'une question. */
    saisirReponse(
        index: number,
        evenement: Event
    ): void {
        this.repondreLibrement(index, (evenement.target as HTMLInputElement).value);
    }

    relireAvecReponses(): void {
        const texte = this.declarationAvecReponses();
        const questions = this.questionsEnMots().map((q) => q.texte);
        const reponse = this.derniere()?.reponse;
        if (!texte || !reponse || this.reponsesTropLongues() || this.chargement()) {
            return;
        }
        const resume = questions
            .map((q, i) => ({ q, r: (this.reponsesLibres()[i] ?? '').trim() }))
            .filter((x) => !!x.r)
            .map((x) => `${x.q} ${x.r}`)
            .join(' ; ');
        // La même méthode que la réponse ; pour la lecture des clauses, les chapitres déjà désignés : la désignation
        // n'est pas redemandée, le dossier est le même (7.218) ; et le jeton de la lecture : seules les clauses en doute
        // sont rejugées (13.4).
        if (reponse.mode === 'clauses') {
            this.analyserTexte(texte, 'clauses', resume, reponse.chapitres, reponse.lecture || undefined);
        } else {
            this.analyserTexte(texte, 'regles', resume);
        }
    }


    // # Plusieurs sinistres (7.222)

    plusieurs(
        r: Decision
    ): boolean {
        return (r.sinistres?.length ?? 0) > 1;
    }

    /** Les réserves d'une décision, ou d'un sinistre : ce que l'assureur pourra vérifier. */
    reservesDe(
        r: Decision
    ): APreciser[] {
        return trierAPreciser(r.a_preciser ?? []).filter((p) => p.nature === 'reserve');
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
        this.api.decider(contratId, fusionner(derniere.reponse.faits, reponses))
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
            this.api.clause(contratId, clauseId)
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
        this.api.fiche(contratId, sinistre.slice(0, 4000), etape.reponse)
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
        this.reponsesLibres.set({});
        this.chargement.set(false);
    }

    private echec(
        erreur: unknown
    ): void {
        this.erreur.set(messageErreur(erreur));
        this.chargement.set(false);
    }
}
