# BR-OBS-CAP-02 — Capacité de support ≠ poids d’un circuit

**Type :** brique réutilisable / interface capacité–circuits  
**Statut :** DÉMONTRÉ (interne RAVI-2)  
**Originalité :** REFORMULATION_SPÉCIALISÉE / INDÉTERMINÉE  
**Dépendance :** `BR-OBS-CAP-01`.

## Domaine

Soit un système `T`, un ensemble de témoins distincts `P(T)`, un mauvais objet `B_p` associé à chaque témoin et une projection géométrique `sh(B_p)=ω`.

Un circuit positif est écrit sur des **objets mauvais distincts** :

`Σ_{B∈C} a_B g_B = 0`, avec `a_B>0`.

Après projection, plusieurs objets distincts peuvent avoir la même ombre `ω` et leurs coefficients sont fusionnés.

## Deux multiplicités différentes

### Multiplicité de support

`r_C(ω) = |{B∈supp(C) : sh(B)=ω}|`.

### Poids projeté

`A_C(ω) = Σ_{B∈supp(C), sh(B)=ω} a_B`.

Ces deux quantités ne sont pas la même chose.

## Théorème — borne de support

Définir

`μ_T(ω) = |{B_p distincts : sh(B_p)=ω}|`.

Alors

`r_C(ω) ≤ μ_T(ω) ≤ ν_T(ω) ≤ Cap(ω)`,

où `ν_T(ω)` est la capacité en témoins distincts de `BR-OBS-CAP-01`.

**Preuve.** Le support du circuit est un sous-ensemble des mauvais objets disponibles. Chaque mauvais objet de projection `ω` est produit par au moins un témoin, donc le nombre d’objets distincts est au plus le nombre de témoins distincts.

## Non-théorème essentiel

En général, on **ne peut pas conclure**

`A_C(ω) ≤ Cap(ω)`.

Le coefficient `a_B` est un poids entier d’un multi-recouvrement et peut être supérieur à 1 sans demander plusieurs témoins distincts. Une borne sur les coefficients exige une hypothèse supplémentaire de type « poids unitaire » ou une interprétation qui transforme explicitement chaque unité de coefficient en témoin différent.

## Conséquence méthodologique

Une capacité dynamique est un filtre sur :

- le nombre de contraintes distinctes disponibles ;
- la taille et l’incidence du support d’un circuit ;
- la coexistence de copies géométriques.

Elle n’est **pas**, à elle seule, une borne sur les coefficients primitifs d’un circuit projeté.

Cette distinction empêche une fausse brique `coefficient ≤ capacité`.

## Application V19

Les circuits V16/V17 utilisent des coefficients entiers de multi-recouvrement. La théorie de capacité V19 peut donc contraindre leur **support dynamique**, mais la comparaison directe `m_i≤Cap(ω_i)` n’est pas certifiée sans information supplémentaire sur l’origine de chaque poids.