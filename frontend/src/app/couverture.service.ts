import {
    inject,
    Injectable
} from '@angular/core';

import {
    HttpClient
} from '@angular/common/http';

import {
    Observable
} from 'rxjs';

import {
    Clause,
    Contrat,
    Decision,
    Faits,
    Sante
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


    clauses(
        contratId: string
    ): Observable<Clause[]> {
        return this.http.get<Clause[]>(
            `${API}/contrats/${encodeURIComponent(contratId)}/clauses`
        );
    }


    /** Une déclaration : le modèle lit les faits, le moteur décide (quelques secondes). */
    analyser(
        contratId: string,
        sinistre: string
    ): Observable<Decision> {
        return this.http.post<Decision>(
            `${API}/analyses`,
            { contrat_id: contratId, sinistre }
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
