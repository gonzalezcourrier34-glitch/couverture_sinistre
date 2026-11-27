import {
    Component,
    inject
} from '@angular/core';

import {
    EchangeService
} from '../echange.service';


/** Les conditions générales à choisir, et les conditions particulières du client (facultatives). */
@Component({
    selector: 'app-choix-contrat',
    imports: [],
    templateUrl: './choix-contrat.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class ChoixContratComponent {

    readonly ech = inject(EchangeService);
}
