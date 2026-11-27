import {
    Component,
    inject,
    input
} from '@angular/core';

import {
    Etape
} from '../couverture.model';

import {
    lisible
} from '../presentation';

import {
    EchangeService,
    LONGUEUR_MAX,
    MAX_PUCES
} from '../echange.service';


/** Ce qu'il faut demander au client, à la dernière étape : avec la chaîne de règles et un seul sinistre, le moteur décide seul ; sinon, les réponses s'ajoutent à la déclaration, relue (7.218, 7.222). */
@Component({
    selector: 'app-questions',
    imports: [],
    templateUrl: './questions.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class QuestionsComponent {

    readonly ech = inject(EchangeService);

    readonly courante = input.required<Etape>();

    readonly derniere = input(false);

    readonly maxPuces = MAX_PUCES;

    readonly longueurMax = LONGUEUR_MAX;

    readonly lisible = lisible;

    /** Les réponses proposées à une question qui n'en a pas : oui ou non, ou la réponse en mots. */
    readonly ouiNon: readonly string[] = ['Oui', 'Non'];
}
