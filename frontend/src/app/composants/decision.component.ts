import {
    Component,
    inject,
    input
} from '@angular/core';

import {
    Decision
} from '../couverture.model';

import {
    LIBELLES,
    TONS,
    lignesDeFaits,
    pourcent
} from '../presentation';

import {
    EchangeService
} from '../echange.service';


/** Une décision : son libellé, la confiance ou l'accord des règles, la phrase, les faits retenus. Pour la déclaration entière, ou pour l'un de ses sinistres. */
@Component({
    selector: 'app-decision',
    imports: [],
    templateUrl: './decision.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class DecisionComponent {

    readonly ech = inject(EchangeService);

    readonly reponse = input.required<Decision>();

    readonly libelles = LIBELLES;

    readonly tons = TONS;

    readonly pourcent = pourcent;

    readonly lignesDeFaits = lignesDeFaits;
}
