import {
    Component,
    inject
} from '@angular/core';

import {
    EchangeService
} from '../echange.service';


/** La fenêtre de l'analyse en cours, étape par étape. */
@Component({
    selector: 'app-suivi',
    imports: [],
    templateUrl: './suivi.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class SuiviComponent {

    readonly ech = inject(EchangeService);
}
