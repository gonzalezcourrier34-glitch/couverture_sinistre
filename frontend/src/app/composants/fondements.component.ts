import {
    Component,
    inject,
    input
} from '@angular/core';

import {
    Decision
} from '../couverture.model';

import {
    citationsParArticle
} from '../presentation';

import {
    EchangeService
} from '../echange.service';


/** Ce qui fonde une décision : les réserves (à la dernière étape), les clauses citées, les limites. */
@Component({
    selector: 'app-fondements',
    imports: [],
    templateUrl: './fondements.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class FondementsComponent {

    readonly ech = inject(EchangeService);

    readonly reponse = input.required<Decision>();

    /** La dernière étape de l'échange : seule elle montre ses réserves. */
    readonly derniere = input(false);

    readonly citationsParArticle = citationsParArticle;
}
