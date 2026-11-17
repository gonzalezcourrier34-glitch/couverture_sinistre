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
    (   regle(definition(N, C, _, _))
    ->  eval(C, E)
    ;   throw(error(existence_error(concept, N), _))
    ).
eval(T, _) :- throw(error(type_error(condition, T), _)).

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
    (   regle(definition(N, C, _, _)) -> variables(C, Vs) ; Vs = [] ).
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
    (   regle(definition(N, C, _, _)) -> feuilles(C, Fs) ; Fs = [] ).
feuilles(_, []).

concepts(concept(N), [N|Ns]) :- !,
    (   regle(definition(N, C, _, _)) -> concepts(C, Ns) ; Ns = [] ).
concepts(non(C), Ns) :- !, concepts(C, Ns).
concepts(et(L), Ns) :- !, maplist(concepts, L, Nss), append(Nss, Ns).
concepts(ou(L), Ns) :- !, maplist(concepts, L, Nss), append(Nss, Ns).
concepts(si(A, B), Ns) :- !, concepts(A, Na), concepts(B, Nb), append(Na, Nb, Ns).
concepts(_, []).

preuve_concept(N, _{article:A, texte:T, role:"définition"}) :- regle(definition(N, _, A, T)).
preuve_concept(N, _{article:A, texte:T, role:"définition"}) :- regle(precision(N, A, T)).

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
classer_exclusion(inconnu, _, oui, C, A, T, x(inconnue, A, T, Q)) :- inconnues(C, Q).

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
    findall(R, ( regle(garantie(G, _, _, _)), evaluer_garantie(G, R) ), Rs),
    combiner(Rs, D0),
    non_traduits(NT),
    plafonner(NT, D0, D1),
    put_dict(garanties, D1, Rs, D).

%  Les événements déclarés dont aucune garantie n'est traduite en règles.
non_traduits(NT) :-
    findall(E, ( fait(evenement, E), E \== autre, \+ regle(evenement_traduit(E)) ), NT0),
    sort(NT0, NT).

plafonner([], D, D) :- !.
plafonner(_, D, D) :- get_dict(decision, D, "COUVERT"), !.
plafonner(NT, D0, D) :- put_dict(_{decision:"INCERTAIN", non_traduits:NT, aucune:false}, D0, D).

% --- Points d'entrée (appelés par src/couverture/prolog.py) --------------------------------------------

ecrire_json(Terme) :-
    json_write_dict(current_output, Terme, [width(0)]),
    nl.

decider_json :- decider(D), ecrire_json(D).

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
