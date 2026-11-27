import {
    Component,
    inject
} from '@angular/core';

import {
    EchangeService
} from '../echange.service';


/** Avant la première analyse : ce que fait la méthode choisie, et les trois réponses possibles. */
@Component({
    selector: 'app-accueil',
    imports: [],
    templateUrl: './accueil.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class AccueilComponent {

    readonly ech = inject(EchangeService);
}
