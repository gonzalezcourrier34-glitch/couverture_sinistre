:- encoding(utf8).
/*  Moteur de décision, commun à tous les contrats.

    Un contrat (regles/<contrat>.pl) est une suite de données :
      definition(Concept, Condition, Article, Texte).
      precision(Concept, Article, Texte).                    % texte de plus à citer
      garantie(Id, Nom, Article, Texte).
      perimetre(Id, Condition).                              % toutes doivent tenir (événement, bien, lieu)
      circonstance(Id, Condition, Article, Texte).           % autres conditions de la garantie
      obligation(Id, Condition, Exception, LienCausal, Article, Texte).
      exclusion(Cible, Condition, Portee, ADemander, Article, Texte).
      limite(Id, Article, Texte, Montant).
      evenement_traduit(Evenement).                          % événements dont les garanties sont en règles

    Une condition est un terme :
      f(Variable, Valeur)   un fait de la déclaration (variables de regles/vocabulaire.json)
      et([...]), ou([...]), non(C), si(A, B), concept(Nom), vrai, faux

    Les faits sont donnés par assertz(fait(Variable, Valeur)) ; une variable sans fait est inconnue.
    Logique à trois valeurs (Kleene) : oui, non, inconnu. Le « je ne sais pas » n'est donc pas
    confondu avec « faux », ce que ferait la négation de Prolog (monde clos).

    Règles de gestionnaire (les mêmes que la méthode « fiches », voir fiches.py) :
      1. périmètre « non »            -> garantie hors sujet ;
      2. circonstance « non »         -> la garantie ne joue pas ;
      3. périmètre « inconnu »        -> garantie possible, on demande ce qui manque ; sauf si une
         exclusion totale est certaine : la garantie est écartée sans question ;
      4. exclusion « oui » (tout)     -> refus ; une exclusion ne vise qu'une garantie rattachée ;
      5. circonstance « inconnu »     -> incertain (c'est à l'assuré d'établir la garantie) ;
      6. obligation non respectée     -> incertain si le refus exige un lien causal, refus sinon ;
      6 bis. exclusion « à demander » entamée (inconnue, mais un de ses faits positifs est établi :
         les travaux sont en cours, le lien causal est inconnu) -> incertain, on demande ce qui manque ;
      7. sinon couvert ; une exclusion « à demander » inconnue est une réserve (charge de la
         preuve : l'assureur prouve l'exclusion) ; une exclusion qui ne vise qu'un bien
         (Portee = bien(B)) n'exclut que ce bien.
      8. un événement déclaré qui n'est pas traduit en règles (ni « autre ») : la décision est au
         plus INCERTAIN. Un refus ne vaut que si toutes les garanties en jeu ont été examinées.
*/

:- use_module(library(lists)).
:- use_module(library(apply)).
:- use_module(library(http/json)).

:- dynamic fait/2.
:- dynamic parent_valeur/3.       % parent_valeur(Variable, Valeur, Parent) : la hiérarchie du vocabulaire
:- dynamic domaine/2.             % domaine(Variable, Valeur) : les valeurs possibles, lues dans vocabulaire.json

%!  regle(+But) : appelle un prédicat du contrat, sans erreur s'il n'en a aucune clause.
regle(But) :-
    functor(But, Nom, Arite),
    current_predicate(Nom/Arite),
    call(But).

% --- Logique à trois valeurs ------------------------------------------------------------------------

eval(vrai, oui) :- !.
eval(faux, non) :- !.
eval(f(V, X), E) :- !,
    (   fait(V, X) -> E = oui
    ;   fait(V, C), ancetre(V, C, X) -> E = oui         % fait précis, règle large : une vitre est un élément du bâtiment
    ;   vague(V, X) -> E = inconnu                       % fait vague, règle précise : « élément du bâtiment » ne dit pas « vitre »
    ;   fait(V, _) -> E = non
    ;   E = inconnu
    ).

eval(non(C), E) :- !, eval(C, E0), inverse(E0, E).
eval(et(L), E) :- !, maplist(eval, L, Es), et3(Es, E).
eval(ou(L), E) :- !, maplist(eval, L, Es), ou3(Es, E).
eval(si(A, B), E) :- !, eval(ou([non(A), B]), E).
eval(concept(N), E) :- !,
    (   condition_concept(N, C)
    ->  eval(C, E)
    ;   throw(error(existence_error(concept, N), _))
    ).
eval(T, _) :- throw(error(type_error(condition, T), _)).

%!  condition_concept(+Concept, -Condition)
%   La définition du contrat, élargie par ses extensions (DEMARCHE 7.69) : « nous étendons la garantie au
%   contenu lors d'un séjour temporaire » élargit le lieu assuré (le bâtiment), pour toutes les garanties qui
%   l'emploient. Une extension ne compte que si elle est établie, ou entamée par la déclaration (le séjour est
%   dit, le lieu ne l'est pas) : elle n'est jamais présumée, et ses faits ne sont pas demandés pour chaque
%   sinistre.
condition_concept(N, C) :-
    regle(definition(N, C0, _, _)), !,
    findall(X, ( regle(extension(N, X, _, _)), extension_active(X) ), Xs),
    (   Xs == [] -> C = C0 ; C = ou([C0|Xs]) ).

extension_active(X) :- eval(X, oui), !.
extension_active(X) :- eval(X, inconnu), propres(X, Fs), member(F, Fs), eval(F, oui), !.

%  Les faits positifs propres à une extension, hors des concepts qu'elle emploie : « contenu » est établi par
%  presque toute déclaration (un meuble), il ne dit rien d'un séjour ou d'un déménagement.
propres(concept(_), []) :- !.
propres(f(V, X), [f(V, X)]) :- !.
propres(et(L), Fs) :- !, maplist(propres, L, Fss), append(Fss, Fs).
propres(ou(L), Fs) :- !, maplist(propres, L, Fss), append(Fss, Fs).
propres(si(_, B), Fs) :- !, propres(B, Fs).
propres(_, []).

%  ancetre(V, X, A) : A est une catégorie plus large que X (vocabulaire, « parents »).
ancetre(V, X, A) :- parent_valeur(V, X, A).
ancetre(V, X, A) :- parent_valeur(V, X, M), ancetre(V, M, A).

%  Un fait déclaré P, plus large que X, et dont aucun fait déclaré ne précise la nature : P ne dit ni oui ni non à X.
vague(V, X) :-
    fait(V, P), ancetre(V, X, P),
    \+ ( fait(V, C), C \== P, ancetre(V, C, P) ).

inverse(oui, non).
inverse(non, oui).
inverse(inconnu, inconnu).

et3(Es, non) :- memberchk(non, Es), !.
et3(Es, inconnu) :- memberchk(inconnu, Es), !.
et3(_, oui).

ou3(Es, oui) :- memberchk(oui, Es), !.
ou3(Es, inconnu) :- memberchk(inconnu, Es), !.
ou3(_, non).

% --- Ce qu'il faudrait savoir, ce qu'il faut citer ----------------------------------------------------

variables(f(V, _), [V]) :- !.
variables(non(C), Vs) :- !, variables(C, Vs).
variables(et(L), Vs) :- !, maplist(variables, L, Vss), append(Vss, Vs).
variables(ou(L), Vs) :- !, maplist(variables, L, Vss), append(Vss, Vs).
variables(si(A, B), Vs) :- !, variables(A, Va), variables(B, Vb), append(Va, Vb, Vs).
variables(concept(N), Vs) :- !,
    (   condition_concept(N, C) -> variables(C, Vs) ; Vs = [] ).
variables(_, []).

%!  inconnues(+Condition, -Variables) : les variables dont un fait élémentaire de la condition est
%   inconnu (pas de fait, ou un fait trop vague) : ce qu'il faut demander.
inconnues(C, Vs) :-
    feuilles(C, Fs),
    findall(V, ( member(f(V, X), Fs), eval(f(V, X), inconnu) ), V0),
    sort(V0, Vs).

feuilles(f(V, X), [f(V, X)]) :- !.
feuilles(non(C), Fs) :- !, feuilles(C, Fs).
feuilles(et(L), Fs) :- !, maplist(feuilles, L, Fss), append(Fss, Fs).
feuilles(ou(L), Fs) :- !, maplist(feuilles, L, Fss), append(Fss, Fs).
feuilles(si(A, B), Fs) :- !, feuilles(A, Fa), feuilles(B, Fb), append(Fa, Fb, Fs).
feuilles(concept(N), Fs) :- !,
    (   condition_concept(N, C) -> feuilles(C, Fs) ; Fs = [] ).
feuilles(_, []).

%!  positives(+Condition, -Feuilles) : les faits qui comptent « pour » la condition : hors d'une
%   négation, et la conclusion d'un « si ». Une condition inconnue dont l'un d'eux est établi est
%   « entamée » : la déclaration l'a mise en jeu (DEMARCHE 7.58).
positives(f(V, X), [f(V, X)]) :- !.
positives(et(L), Fs) :- !, maplist(positives, L, Fss), append(Fss, Fs).
positives(ou(L), Fs) :- !, maplist(positives, L, Fss), append(Fss, Fs).
positives(si(_, B), Fs) :- !, positives(B, Fs).
positives(concept(N), Fs) :- !,
    (   regle(definition(N, C, _, _)) -> positives(C, Fs) ; Fs = [] ).   % la définition seule : pas de boucle
positives(_, []).

entamee(C) :- positives(C, Fs), member(F, Fs), eval(F, oui), !.

concepts(concept(N), [N|Ns]) :- !,
    (   condition_concept(N, C) -> concepts(C, Ns) ; Ns = [] ).
concepts(non(C), Ns) :- !, concepts(C, Ns).
concepts(et(L), Ns) :- !, maplist(concepts, L, Nss), append(Nss, Ns).
concepts(ou(L), Ns) :- !, maplist(concepts, L, Nss), append(Nss, Ns).
concepts(si(A, B), Ns) :- !, concepts(A, Na), concepts(B, Nb), append(Na, Nb, Ns).
concepts(_, []).

preuve_concept(N, _{article:A, texte:T, role:"définition"}) :- regle(definition(N, _, A, T)).
preuve_concept(N, _{article:A, texte:T, role:"définition"}) :- regle(precision(N, A, T)).
preuve_concept(N, _{article:A, texte:T, role:"extension"}) :- regle(extension(N, X, A, T)), eval(X, oui).

%!  preuves_conditions(+Conditions, -Preuves) : les définitions citées par ces conditions.
preuves_conditions(Cs, Preuves) :-
    findall(P, ( member(C, Cs), concepts(C, Ns), member(N, Ns), preuve_concept(N, P) ), P0),
    list_to_set(P0, Preuves).

% --- Une garantie ---------------------------------------------------------------------------------

evaluer_garantie(G, R) :-
    regle(garantie(G, Nom, Art, Texte)),
    findall(C, regle(perimetre(G, C)), Ps),
    maplist(eval, Ps, EPs),
    et3(EPs, EP),
    findall(c(C, A, T, E), ( regle(circonstance(G, C, A, T)), eval(C, E) ), Cs),
    exclusions(G, Xs),
    obligations(G, Os),
    issue(G, EP, Ps, EPs, Cs, Xs, Os, Art, Texte, I),
    !,
    put_dict(I, _{id:G, garantie:Nom, article:Art}, R).

exclusions(G, Xs) :-
    findall(X,
            ( regle(exclusion(Cible, C, Portee, Dem, A, T)),
              vise(Cible, G),
              eval(C, E),
              classer_exclusion(E, Portee, Dem, C, A, T, X) ),
            Xs).

vise(tous, _) :- !.
vise(G, G) :- !.
vise(Liste, G) :- is_list(Liste), memberchk(G, Liste).

classer_exclusion(oui, tout, _, _, A, T, x(totale, A, T, [])) :- !.
classer_exclusion(oui, bien(B), _, _, A, T, X) :- !,
    (   fait(bien, Autre), Autre \== B, \+ ancetre(bien, B, Autre), \+ ancetre(bien, Autre, B)
    ->  X = x(partielle, A, T, B)          % d'autres biens sont touchés : seul B est exclu
    ;   X = x(totale, A, T, [])
    ).
classer_exclusion(inconnu, _, oui, C, A, T, X) :-
    inconnues(C, Q),
    (   entamee(C) -> X = x(engagee, A, T, Q) ; X = x(inconnue, A, T, Q) ).

obligations(G, Os) :-
    findall(o(E, L, A, T, C),
            ( regle(obligation(G, C, Exception, L, A, T)), etat_obligation(C, Exception, E) ),
            Os).

etat_obligation(C, Exception, E) :-
    eval(Exception, EE),
    (   EE == oui -> E = oui                % ex. « en cas d'effraction, sans incidence »
    ;   eval(C, E)
    ).

preuve(A, T, Role, _{article:A, texte:T, role:Role}).

%  issue(+G, +EtatPerimetre, +Ps, +EPs, +Circonstances, +Exclusions, +Obligations, +Art, +Texte, -Issue)
issue(_, non, Ps, EPs, _, _, _, Art, Texte, I) :- !,
    findall(P, ( nth1(K, EPs, non), nth1(K, Ps, P) ), Ko),
    preuves_conditions(Ko, Pr),
    preuve(Art, Texte, "garantie", PG),
    I = _{rattachement:"hors", decision:"NON_COUVERT", motif:"hors de son périmètre",
          preuves:[PG|Pr], questions:[], reserves:[], partielles:[]}.
issue(_, _, _, _, Cs, _, _, _, _, I) :-
    member(c(_, A, T, non), Cs), !,
    preuve(A, T, "condition", P),
    I = _{rattachement:"rattachée", decision:"NON_COUVERT", motif:"une condition n'est pas remplie",
          preuves:[P], questions:[], reserves:[], partielles:[]}.
%  Une exclusion certaine écarte la garantie même si l'on ne sait pas encore si elle s'appliquerait :
%  un vol dans le casier du club est exclu, inutile de demander s'il a été commis sur la personne.
issue(_, inconnu, _, _, _, Xs, _, _, _, I) :-
    member(x(totale, A, T, _), Xs), !,
    preuve(A, T, "exclusion", P),
    I = _{rattachement:"rattachée", decision:"NON_COUVERT", motif:"une exclusion s'applique",
          preuves:[P], questions:[], reserves:[], partielles:[]}.
issue(_, inconnu, Ps, _, Cs, _, _, Art, Texte, I) :- !,
    inconnues(et(Ps), Q1),
    findall(V, ( member(c(C, _, _, inconnu), Cs), inconnues(C, Vs), member(V, Vs) ), Q2),
    append(Q1, Q2, Q0), sort(Q0, Q),
    preuve(Art, Texte, "garantie", PG),
    I = _{rattachement:"possible", decision:"INCERTAIN",
          motif:"pourrait s'appliquer, selon des faits non précisés",
          preuves:[PG], questions:Q, reserves:[], partielles:[]}.
issue(_, oui, _, _, _, Xs, _, _, _, I) :-
    member(x(totale, A, T, _), Xs), !,
    preuve(A, T, "exclusion", P),
    I = _{rattachement:"rattachée", decision:"NON_COUVERT", motif:"une exclusion s'applique",
          preuves:[P], questions:[], reserves:[], partielles:[]}.
issue(_, oui, _, _, Cs, _, _, _, _, I) :-
    member(c(C, A, T, inconnu), Cs), !,
    inconnues(C, Q),
    preuve(A, T, "condition", P),
    I = _{rattachement:"rattachée", decision:"INCERTAIN", motif:"s'applique, selon des faits non précisés",
          preuves:[P], questions:Q, reserves:[], partielles:[]}.
issue(_, oui, _, _, _, Xs, _, _, _, I) :-
    member(x(engagee, A, T, _), Xs), !,
    findall(V, ( member(x(engagee, _, _, Vs), Xs), member(V, Vs) ), Q0), sort(Q0, Q),
    preuve(A, T, "exclusion", P),
    I = _{rattachement:"rattachée", decision:"INCERTAIN",
          motif:"une exclusion est en jeu, selon des faits non précisés",
          preuves:[P], questions:Q, reserves:[], partielles:[]}.
issue(_, oui, _, _, _, _, Os, _, _, I) :-
    member(o(non, oui, A, T, _), Os), !,
    preuve(A, T, "obligation", P),
    I = _{rattachement:"rattachée", decision:"INCERTAIN",
          motif:"une obligation de prévention n'est pas respectée : refus seulement s'il y a un lien causal avec le sinistre",
          preuves:[P], questions:[lien_causal], reserves:[], partielles:[]}.
issue(_, oui, _, _, _, _, Os, _, _, I) :-
    member(o(non, non, A, T, _), Os), !,
    preuve(A, T, "obligation", P),
    I = _{rattachement:"rattachée", decision:"NON_COUVERT",
          motif:"une obligation de prévention n'est pas respectée",
          preuves:[P], questions:[], reserves:[], partielles:[]}.
issue(G, oui, Ps, _, Cs, Xs, Os, Art, Texte, I) :-
    findall(V, ( member(x(inconnue, _, _, Vs), Xs), member(V, Vs) ), R1),
    findall(V, ( member(o(inconnu, _, _, _, C), Os), inconnues(C, Vs), member(V, Vs) ), R2),
    append(R1, R2, R0), sort(R0, Reserves),
    findall(_{article:A, texte:T, role:"exclusion partielle", bien:B}, member(x(partielle, A, T, B), Xs), Parts),
    preuve(Art, Texte, "garantie", PG),
    preuves_conditions(Ps, PD),
    findall(P, ( member(c(_, A, T, oui), Cs), preuve(A, T, "condition", P) ), PC),
    findall(_{article:A, texte:T, role:"limite", montant:M}, regle(limite(G, A, T, M)), Lim),
    append([[PG], PD, PC], Preuves),
    (   Parts == [] -> M0 = "s'applique : périmètre et conditions établis"
    ;   M0 = "s'applique, sauf pour les biens exclus ci-dessous"
    ),
    (   Reserves == [] -> Motif = M0
    ;   string_concat(M0, " ; sous réserve des vérifications à faire", Motif)
    ),
    I = _{rattachement:"rattachée", decision:"COUVERT", motif:Motif, preuves:Preuves,
          questions:[], reserves:Reserves, partielles:Parts, limites:Lim}.

% --- Toutes les garanties ---------------------------------------------------------------------------

%  COUVERT si une garantie rattachée l'est ; sinon INCERTAIN si une rattachée l'est ; sinon refus si une
%  rattachée refuse (les garanties seulement « possibles » ajoutent leurs questions) ; sinon INCERTAIN
%  si une garantie est possible ; sinon refus (aucune garantie ne s'applique) ; sinon INCERTAIN.
combiner(Rs, D) :-
    include(rattachement("rattachée"), Rs, Ratt),
    include(rattachement("possible"), Rs, Poss),
    (   include(decision_est("COUVERT"), Ratt, [C|_])
    ->  D = _{decision:"COUVERT", retenues:[C], possibles:[]}
    ;   include(decision_est("INCERTAIN"), Ratt, In), In \== []
    ->  D = _{decision:"INCERTAIN", retenues:In, possibles:Poss}
    ;   Ratt \== []
    ->  D = _{decision:"NON_COUVERT", retenues:Ratt, possibles:Poss}
    ;   Poss \== []
    ->  D = _{decision:"INCERTAIN", retenues:Poss, possibles:[]}
    ;   Rs \== []
    ->  D = _{decision:"NON_COUVERT", retenues:Rs, possibles:[], aucune:true}
    ;   D = _{decision:"INCERTAIN", retenues:[], possibles:[]}
    ).

rattachement(V, R) :- get_dict(rattachement, R, V).
decision_est(V, R) :- get_dict(decision, R, V).

decider(D) :-
    findall(R, ( regle(garantie(G, _, _, _)), \+ regle(accessoire(G)), evaluer_garantie(G, R) ), Rs),
    combiner(Rs, D0),
    non_traduits(NT),
    plafonner(NT, D0, D1),
    accessoires(D1, Acc),
    put_dict(_{garanties:Rs, accessoires:Acc}, D1, D).

%!  accessoires(+Decision, -Accessoires)
%   Une garantie accessoire (frais de sauvetage, logement provisoire, extension en séjour : DEMARCHE 7.68)
%   ne joue qu'après un sinistre couvert par une garantie de base. Elle ne change jamais la décision : si la
%   décision est COUVERT, on liste celles dont le périmètre est établi (le séjour, le déménagement : faits
%   déclarés), avec leurs questions et réserves ; sinon, aucune. Une accessoire au périmètre seulement
%   possible n'est pas listée : sans cela, chaque incendie couvert énumérait toutes les extensions de Foyer 3.1. Traduites comme des garanties ordinaires, elles faisaient passer des refus justes à
%   « incertain » (25 cas au contrôle de non-régression du lot B de Foyer).
accessoires(D, Acc) :-
    get_dict(decision, D, "COUVERT"), !,
    findall(R, ( regle(accessoire(G)), evaluer_garantie(G, R),
                 get_dict(rattachement, R, "rattachée"), \+ get_dict(decision, R, "NON_COUVERT") ), Acc).
accessoires(_, []).

%  Les événements déclarés dont aucune garantie n'est traduite en règles.
non_traduits(NT) :-
    findall(E, ( fait(evenement, E), E \== autre, \+ regle(evenement_traduit(E)) ), NT0),
    sort(NT0, NT).

plafonner([], D, D) :- !.
plafonner(_, D, D) :- get_dict(decision, D, "COUVERT"), !.
plafonner(NT, D0, D) :- put_dict(_{decision:"INCERTAIN", non_traduits:NT, aucune:false}, D0, D).

% --- Arbre de preuve : pourquoi cette décision ------------------------------------------------------
/*  Pour chaque garantie retenue, l'arbre de ce que le moteur a évalué : périmètre, conditions,
    obligations, exclusions, chacune avec sa phrase du contrat, son état (oui, non, inconnu) et ses
    sous-conditions jusqu'aux faits déclarés. C'est la trace de la déduction elle-même, pas une
    explication écrite après coup : chaque nœud est recalculé avec le même eval/2 que la décision.
*/

%!  arbre(+Condition, -Noeud)
arbre(C, T) :- eval(C, E), arbre_noeud(C, E, T).

arbre_noeud(f(V, X), E, _{type:"fait", variable:V, attendu:X, declare:Ds, etat:E, enfants:[]}) :- !,
    findall(D, fait(V, D), D0), sort(D0, Ds).
arbre_noeud(non(C), E, _{type:"non", etat:E, enfants:[T]}) :- !, arbre(C, T).
arbre_noeud(et(L), E, _{type:"et", etat:E, enfants:Ts}) :- !, maplist(arbre, L, Ts).
arbre_noeud(ou(L), E, _{type:"ou", etat:E, enfants:Ts}) :- !, maplist(arbre, L, Ts).
arbre_noeud(si(A, B), E, _{type:"si", etat:E, enfants:[TA, TB]}) :- !, arbre(A, TA), arbre(B, TB).
arbre_noeud(concept(N), E, _{type:"concept", nom:N, article:A, texte:Tx, etat:E, enfants:[T]}) :- !,
    once(regle(definition(N, _, A, Tx))), condition_concept(N, C), arbre(C, T).
arbre_noeud(vrai, E, _{type:"vrai", etat:E, enfants:[]}) :- !.
arbre_noeud(faux, E, _{type:"faux", etat:E, enfants:[]}).

etat_noeud(T, E) :- get_dict(etat, T, E).

%!  arbre_garantie(+Garantie, -Noeud) : une garantie hors de son périmètre ne montre que son périmètre.
arbre_garantie(G, _{type:"garantie", id:G, nom:Nom, article:A, texte:T, decision:Dec, enfants:Es}) :-
    regle(garantie(G, Nom, A, T)),
    evaluer_garantie(G, R),
    get_dict(decision, R, Dec),
    findall(N, ( regle(perimetre(G, C)), arbre(C, TC), etat_noeud(TC, E),
                 N = _{type:"périmètre", etat:E, enfants:[TC]} ), Ps),
    (   get_dict(rattachement, R, "hors")
    ->  Es = Ps
    ;   findall(N, ( regle(circonstance(G, C, A1, T1)), arbre(C, TC), etat_noeud(TC, E),
                     N = _{type:"condition", article:A1, texte:T1, etat:E, enfants:[TC]} ), Cs),
        findall(N, ( regle(obligation(G, C, X, _, A1, T1)), etat_obligation(C, X, E),
                     arbre(C, TC), arbre(X, TX),
                     N = _{type:"obligation", article:A1, texte:T1, etat:E, enfants:[TC], exception:TX} ), Os),
        findall(N, ( regle(exclusion(Cible, C, _, Dem, A1, T1)), vise(Cible, G), arbre(C, TC), etat_noeud(TC, E),
                     N = _{type:"exclusion", article:A1, texte:T1, a_demander:Dem, etat:E, enfants:[TC]} ), Xs),
        append([Ps, Cs, Os, Xs], Es)
    ).

%!  arbres_de_preuve(+Decision, -Arbres) : un arbre par garantie retenue.
arbres_de_preuve(D, Ts) :-
    get_dict(retenues, D, Rs),
    findall(G, ( member(R, Rs), get_dict(id, R, G) ), G0),
    list_to_set(G0, Gs),
    maplist(arbre_garantie, Gs, Ts).

% --- Raisonnement par hypothèses : quelles questions comptent ? --------------------------------------
/*  Quand la décision dépend de faits inconnus, le moteur ne se contente pas de lister les questions :
    il **essaie chaque réponse possible** (assertz, décision, retract) et classe chaque question :
      - décisive : chaque réponse donne une décision ferme (« oui → COUVERT, non → NON_COUVERT ») ;
      - utile    : une réponse au moins change la décision, sans toujours trancher seule ;
      - inutile  : quelle que soit la réponse, la décision ne change pas : on ne la pose pas.
    Sans question décisive, il cherche une paire de questions qui tranche toujours.
    C'est du raisonnement hypothétique sur les mêmes règles : ce pour quoi Prolog est fait.        */

charger_domaines(Fichier) :-
    retractall(domaine(_, _)),
    setup_call_cleanup(open(Fichier, read, S, [encoding(utf8)]), json_read_dict(S, J), close(S)),
    get_dict(variables, J, Vars),
    forall(( get_dict(V, Vars, Def), get_dict(valeurs, Def, Xs), member(X0, Xs), atom_string(X, X0) ),
           assertz(domaine(V, X))).

%  Les variables demandées par la décision (questions et réserves), qui ont un domaine connu.
questions_posees(D, Vs) :-
    get_dict(retenues, D, Rs),
    ( get_dict(possibles, D, Ps) -> true ; Ps = [] ),
    findall(V, ( member(R, Rs), ( get_dict(questions, R, Q) ; get_dict(reserves, R, Q) ), member(V, Q) ), V1),
    findall(V, ( member(P, Ps), get_dict(questions, P, Q), member(V, Q) ), V2),
    append(V1, V2, V0),
    include(a_un_domaine, V0, V3),
    list_to_set(V3, Vs).

a_un_domaine(V) :- atom(V), domaine(V, _), !.

%  Les valeurs à essayer : tout le domaine ; ou, si un fait vague existe déjà, ses précisions.
valeurs_a_essayer(V, Xs) :-
    (   fait(V, _)
    ->  findall(X, ( domaine(V, X), \+ fait(V, X), fait(V, P), ancetre(V, X, P) ), X0)
    ;   findall(X, domaine(V, X), X0)
    ),
    sort(X0, Xs).

%  essai(+Hypotheses, -Decision) : la décision si l'on ajoute ces faits ; rien n'est laissé derrière.
essai(Hyps, Dec) :-
    forall(member(V=X, Hyps), assertz(fait(V, X))),
    (   catch(decider(D), _, fail) -> get_dict(decision, D, Dec) ; Dec = "ERREUR" ),
    forall(member(V=X, Hyps), retract(fait(V, X))).

ferme(Dec) :- Dec \== "INCERTAIN", Dec \== "ERREUR".

explorer_question(Courante, V, Q) :-
    valeurs_a_essayer(V, Xs), Xs \== [],
    findall(X-Dec, ( member(X, Xs), essai([V=X], Dec) ), Paires),
    findall(Dec, member(_-Dec, Paires), Ds0), sort(Ds0, Ds),
    (   forall(member(Dec, Ds), ferme(Dec)), Ds = [_, _|_] -> Effet = "décisive"
    ;   forall(member(Dec, Ds), ferme(Dec)), Ds = [Seule], Seule \== Courante -> Effet = "décisive"
    ;   Ds \== [Courante] -> Effet = "utile"
    ;   Effet = "inutile"
    ),
    findall(_{decision:Dec, valeurs:Vals},
            ( member(Dec, Ds), findall(X, member(X-Dec, Paires), Vals) ), Issues),
    Q = _{variable:V, effet:Effet, issues:Issues}.

rang("décisive", 0).
rang("utile", 1).
rang("inutile", 2).

%  Une paire de questions dont toutes les réponses croisées donnent une décision ferme (bornée à 400 essais).
paire_decisive(Vs, [V1, V2]) :-
    append(_, [V1|Reste], Vs), member(V2, Reste),
    valeurs_a_essayer(V1, X1s), valeurs_a_essayer(V2, X2s),
    length(X1s, N1), length(X2s, N2), N1 * N2 =< 400,
    forall(( member(X1, X1s), member(X2, X2s) ), ( essai([V1=X1, V2=X2], Dec), ferme(Dec) )), !.

explorer(D, _{questions:Qs, ensemble:Ens}) :-
    get_dict(decision, D, Courante),
    questions_posees(D, Vs),
    findall(R-Q, ( member(V, Vs), explorer_question(Courante, V, Q), get_dict(effet, Q, E), rang(E, R) ), RQs),
    keysort(RQs, Tries), pairs_values(Tries, Qs),
    (   member(Q, Qs), get_dict(effet, Q, "décisive") -> get_dict(variable, Q, V0), Ens = [V0]
    ;   findall(V, ( member(Q, Qs), get_dict(effet, Q, "utile"), get_dict(variable, Q, V) ), Utiles),
        paire_decisive(Utiles, Paire) -> Ens = Paire
    ;   Ens = []
    ).

% --- Points d'entrée (appelés par src/couverture/prolog.py) --------------------------------------------

ecrire_json(Terme) :-
    json_write_dict(current_output, Terme, [width(0)]),
    nl.

decider_json :-
    decider(D0),
    (   domaine(_, _), questions_posees(D0, [_|_])
    ->  explorer(D0, E), put_dict(exploration, D0, E, D1)
    ;   D1 = D0
    ),
    arbres_de_preuve(D1, P),
    put_dict(preuve, D1, P, D),
    ecrire_json(D).

%!  servir : le moteur reste chargé et décide à la demande (DEMARCHE 7.46).
%   Chaque demande est un terme sur l'entrée standard : faits([Variable-Valeur, ...]). La réponse est une
%   ligne JSON (la décision, ou {"erreur": ...}). `pret.` répond {"pret": true} : Python s'en sert pour savoir
%   que le moteur et les règles sont chargés. La fin de l'entrée arrête la boucle.
servir :-
    prompt(_, ''),                       % pas d'invite « |: » dans la réponse
    set_stream(user_input, encoding(utf8)),
    set_stream(user_output, encoding(utf8)),
    repeat,
    catch(read_term(user_input, T, []), E, T = illisible(E)),
    (   T == end_of_file
    ->  !
    ;   servir_un(T),
        flush_output,
        fail
    ).

servir_un(pret) :- !,
    ecrire_json(_{pret:true}).
servir_un(faits(Fs)) :- !,
    retractall(fait(_, _)),
    forall(member(V-X, Fs), assertz(fait(V, X))),
    (   catch(decider_json, E, ( format(string(Texte), "~q", [E]), ecrire_json(_{erreur:Texte}) ))
    ->  true
    ;   ecrire_json(_{erreur:"la décision a échoué"})
    ),
    retractall(fait(_, _)).
servir_un(T) :-
    format(string(Texte), "demande inconnue : ~q", [T]),
    ecrire_json(_{erreur:Texte}).

%  Les couples (variable, valeur) employés par le contrat : comparés au vocabulaire par Python.
vocabulaire_json :-
    findall(_{variable:V, valeur:X}, ( condition_du_contrat(C), feuille(C, f(V, X)) ), L0),
    list_to_set(L0, L),
    ecrire_json(L).

%  Toutes les citations du contrat : vérifiées dans le texte des CG par Python.
citations_json :-
    findall(_{article:A, texte:T}, citation(A, T), L0),
    list_to_set(L0, L),
    ecrire_json(L).

condition_du_contrat(C) :- regle(definition(_, C, _, _)).
condition_du_contrat(C) :- regle(perimetre(_, C)).
condition_du_contrat(C) :- regle(circonstance(_, C, _, _)).
condition_du_contrat(C) :- regle(obligation(_, C, _, _, _, _)).
condition_du_contrat(C) :- regle(obligation(_, _, C, _, _, _)).
condition_du_contrat(C) :- regle(exclusion(_, C, _, _, _, _)).
condition_du_contrat(f(bien, B)) :- regle(exclusion(_, _, bien(B), _, _, _)).
condition_du_contrat(f(evenement, E)) :- regle(evenement_traduit(E)).

feuille(f(V, X), f(V, X)).
feuille(non(C), F) :- feuille(C, F).
feuille(et(L), F) :- member(C, L), feuille(C, F).
feuille(ou(L), F) :- member(C, L), feuille(C, F).
feuille(si(A, B), F) :- ( feuille(A, F) ; feuille(B, F) ).

citation(A, T) :- regle(definition(_, _, A, T)).
citation(A, T) :- regle(precision(_, A, T)).
citation(A, T) :- regle(garantie(_, _, A, T)).
citation(A, T) :- regle(circonstance(_, _, A, T)).
citation(A, T) :- regle(obligation(_, _, _, _, A, T)).
citation(A, T) :- regle(exclusion(_, _, _, _, A, T)).
citation(A, T) :- regle(limite(_, A, T, _)).
