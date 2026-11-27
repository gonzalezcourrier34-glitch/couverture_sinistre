import {
    Component,
    inject,
    input
} from '@angular/core';

import {
    KeyValuePipe
} from '@angular/common';

import {
    Etape
} from '../couverture.model';

import {
    DecisionComponent
} from './decision.component';

import {
    FondementsComponent
} from './fondements.component';

import {
    QuestionsComponent
} from './questions.component';

import {
    EchangeService
} from '../echange.service';


/** Une étape de l'échange : la déclaration ou les réponses, la décision (une par sinistre s'il y en a plusieurs), les questions, ce qui la fonde, la fiche, le raisonnement. */
@Component({
    selector: 'app-etape',
    imports: [KeyValuePipe, DecisionComponent, FondementsComponent, QuestionsComponent],
    templateUrl: './etape.component.html',
    // Le composant ne crée pas de boîte : ses éléments prennent place dans la mise en page de l'écran, comme avant (13.1).
    host: { style: 'display: contents' }
})
export class EtapeComponent {

    readonly ech = inject(EchangeService);

    readonly courante = input.required<Etape>();

    readonly derniere = input(false);
}
