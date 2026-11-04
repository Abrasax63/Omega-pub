# Définitions actives — version 0.1

## 1. Système réflexif fini minimal

Un système réflexif fini déterministe est un quintuple

\[
R=(X,M,U,h,z_0),
\]

où :

- `X` est un ensemble fini d’états objets ;
- `M` est un ensemble fini d’états méta ou de représentations internes ;
- `U : X × M → X × M` est la transition globale ;
- `h : X × M → O` est l’observation ;
- `z_0=(x_0,m_0)` est l’état initial.

Cette définition est volontairement faible : elle n’exige pas encore que `M` code effectivement `U` ni que le système puisse modifier son propre interpréteur.

## 2. Système non réflexif fini

Un système non réflexif fini déterministe est un quadruple

\[
N=(Y,V,g,y_0),
\]

où `Y` est fini, `V:Y→Y`, `g:Y→O` et `y_0∈Y`.

## 3. Trace observable

La trace de longueur `T` est

\[
\operatorname{tr}_T(S)=(o_0,o_1,\ldots,o_T),
\]

avec observation de l’état initial puis des états obtenus par itération de la transition.

## 4. Équivalence de traces

Deux systèmes sont équivalents pour l’état initial considéré lorsque leurs traces sont identiques pour toute longueur finie `T`.

## 5. Coûts à ne pas confondre

- `C_state` : nombre de bits nécessaires pour identifier l’état courant ;
- `C_desc` : longueur de description de la transition et de l’observation ;
- `C_time(T)` : temps nécessaire pour produire les `T` premières transitions ;
- `C_work` : mémoire de travail supplémentaire ;
- `C_update` : coût d’une modification de la représentation ou du mécanisme exécutif.

Aucun « gain de capacité » ne sera défini avant le choix d’un vecteur de coûts et d’un ordre de comparaison.

## 6. Réflexivité forte — à formaliser ensuite

Une version forte devra distinguer au minimum :

1. une représentation `code(U)` accessible dans `M` ;
2. une fonction d’interprétation explicitée ;
3. une opération autorisée de transformation de ce code ;
4. une règle reliant le code modifié à la transition future.

Sans ces conditions, `M` n’est qu’un état auxiliaire, pas nécessairement une représentation réflexive.