import {
    Component,
    OnInit,
    inject
} from '@angular/core';

import {
    EchangeService
} from './echange.service';

import {
    AccueilComponent
} from './composants/accueil.component';

import {
    ArticleComponent
} from './composants/article.component';

import {
    ChoixContratComponent
} from './composants/choix-contrat.component';

import {
    EnTeteComponent
} from './composants/en-tete.component';

import {
    EtapeComponent
} from './composants/etape.component';

import {
    SaisieComponent
} from './composants/saisie.component';

import {
    SuiviComponent
} from './composants/suivi.component';


/*
 * L'écran : la mise en page seule (13.1). Chaque bloc est un composant, et tous lisent le même état, l'échange en
 * cours (`EchangeService`) : le contrat, la déclaration, les étapes, les réponses du client, les fenêtres. Les styles
 * de l'écran sont globaux (`src/ecran.scss`) : les composants ne créent pas de boîte, la mise en page est celle d'avant.
 */

@Component({
    selector: 'app-root',
    imports: [AccueilComponent, ArticleComponent, ChoixContratComponent, EnTeteComponent, EtapeComponent,
        SaisieComponent, SuiviComponent],
    templateUrl: './app.component.html',
    host: {
        '(document:keydown.escape)': 'ech.fermerArticle()'
    }
})
export class AppComponent implements OnInit {

    readonly ech = inject(EchangeService);

    ngOnInit(): void {
        this.ech.demarrer();
    }
}
