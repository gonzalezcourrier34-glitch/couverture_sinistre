import {
    Component,
    inject
} from '@angular/core';

import {
    EchangeService
} from '../echange.service';


/** L'en-tête : le titre, la méthode en une phrase, l'état du service et ses modèles. */
@Component({
    selector: 'app-en-tete',
    imports: [],
    templateUrl: './en-tete.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class EnTeteComponent {

    readonly ech = inject(EchangeService);
}
