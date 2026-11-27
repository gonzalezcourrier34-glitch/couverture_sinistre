import {
    Component,
    inject
} from '@angular/core';

import {
    surligner
} from '../presentation';

import {
    EchangeService
} from '../echange.service';


/** L'article cité, en entier, dans une fenêtre ; les passages cités surlignés. */
@Component({
    selector: 'app-article',
    imports: [],
    templateUrl: './article.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class ArticleComponent {

    readonly ech = inject(EchangeService);

    readonly surligner = surligner;
}
