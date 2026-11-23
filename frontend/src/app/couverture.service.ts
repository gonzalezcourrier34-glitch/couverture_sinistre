import {
    inject,
    Injectable
} from '@angular/core';

import {
    HttpClient,
    HttpErrorResponse
} from '@angular/common/http';

import {
    Observable
} from 'rxjs';

import {
    Clause,
    Contrat,
    Decision,
    Faits,
    Sante,
    Suivi
} from './couverture.model';


// # Configuration (le proxy Angular envoie /api vers FastAPI, avec la clé)

const API = '/api/v1';


// # Service

@Injectable({
    providedIn: 'root'
})
export class CouvertureService {

    private readonly http = inject(
        HttpClient
    );


    sante(): Observable<Sante> {
        return this.http.get<Sante>(`${API}/sante`);
    }


    contrats(): Observable<Contrat[]> {
        return this.http.get<Contrat[]>(`${API}/contrats`);
    }


    /** Une clause citée, pour en lire l'article entier. L'identifiant peut contenir « / » (« 12/batiment »). */
    clause(
        contratId: string,
        clauseId: string
    ): Observable<Clause> {
        const chemin = clauseId.split('/').map(encodeURIComponent).join('/');
        return this.http.get<Clause>(
            `${API}/contrats/${encodeURIComponent(contratId)}/clauses/${chemin}`
        );
    }


    /** Une déclaration : le modèle lit les faits, le moteur décide (quelques secondes). */
    analyser(
        contratId: string,
        sinistre: string,
        souscription: Record<string, string> = {}
    ): Observable<Decision> {
        return this.http.post<Decision>(
            `${API}/analyses`,
            { contrat_id: contratId, sinistre, souscription }
        );
    }


    /**
     * La même analyse, racontée pendant qu'elle se fait : l'API envoie une ligne JSON par étape, puis la décision.
     * `fetch` plutôt que `HttpClient` : il donne le flux au fur et à mesure. Se désabonner interrompt l'appel.
     */
    analyserAvecSuivi(
        contratId: string,
        sinistre: string,
        souscription: Record<string, string> = {}
    ): Observable<Suivi> {
        return new Observable<Suivi>((abonne) => {
            const arret = new AbortController();
            const lire = async (): Promise<void> => {
                const reponse = await fetch(`${API}/analyses/suivi`, {
                    method: 'POST',
                    headers: { 'content-type': 'application/json' },
                    body: JSON.stringify({ contrat_id: contratId, sinistre, souscription }),
                    signal: arret.signal
                });
                if (!reponse.ok || !reponse.body) {
                    const corps: unknown = await reponse.json().catch(() => null);
                    throw new HttpErrorResponse({ status: reponse.status, error: corps });
                }
                const lecteur = reponse.body.getReader();
                const decodeur = new TextDecoder();
                let reste = '';
                for (;;) {
                    const { done, value } = await lecteur.read();
                    if (done) {
                        break;
                    }
                    reste += decodeur.decode(value, { stream: true });
                    const lignes = reste.split('\n');
                    reste = lignes.pop() ?? '';
                    for (const ligne of lignes) {
                        if (ligne.trim()) {
                            abonne.next(JSON.parse(ligne) as Suivi);
                        }
                    }
                }
                if (reste.trim()) {
                    abonne.next(JSON.parse(reste) as Suivi);
                }
                abonne.complete();
            };
            lire().catch((erreur: unknown) => {
                if (!arret.signal.aborted) {
                    abonne.error(erreur instanceof HttpErrorResponse ? erreur : new HttpErrorResponse({ status: 0 }));
                }
            });
            return () => arret.abort();
        });
    }

    /** La fiche d'une décision, en PDF : la réponse est renvoyée telle quelle, rien n'est recalculé. */
    fiche(
        contratId: string,
        sinistre: string,
        reponse: Decision
    ): Observable<Blob> {
        return this.http.post(
            `${API}/fiches`,
            { contrat_id: contratId, sinistre, reponse },
            { responseType: 'blob' }
        );
    }

    /** Des faits : le moteur seul décide (quelques millisecondes, sans modèle). */
    decider(
        contratId: string,
        faits: Faits
    ): Observable<Decision> {
        return this.http.post<Decision>(
            `${API}/decisions`,
            { contrat_id: contratId, faits }
        );
    }
}
