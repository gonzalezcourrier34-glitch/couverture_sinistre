import {
    Component,
    inject
} from '@angular/core';

import {
    EchangeService,
    EXEMPLES,
    LONGUEUR_MAX
} from '../echange.service';


/** La déclaration du client : la méthode, la saisie, les exemples, « Analyser ». */
@Component({
    selector: 'app-saisie',
    imports: [],
    templateUrl: './saisie.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class SaisieComponent {

    readonly ech = inject(EchangeService);

    readonly exemples = EXEMPLES;

    readonly longueurMax = LONGUEUR_MAX;
}
