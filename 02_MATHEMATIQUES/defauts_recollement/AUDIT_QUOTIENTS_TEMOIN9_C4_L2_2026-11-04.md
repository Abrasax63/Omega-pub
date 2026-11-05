# Audit complémentaire — quotients du témoin C4, L=2 à 9 états

Date : 2026-11-04  
Branche : `pilot/ravi2-extraction-c4-20261104`  
Statut : **CALCUL EXACT** sous la définition primaire V19(2) raccordée au contrat du pilote.

## 1. Question

Le témoin `T=(1,2,3,0,8,7,6,2,0)` peut-il être réduit par un quotient de congruence tout en conservant le cycle C4, les huit paires, la cohérence forcée et les huit ombres exactes ?

## 2. Génération des congruences

Deux procédures ont été réimplémentées séparément :
1. fermeture par fusions successives, propagées par l'image de T ;
2. énumération de toutes les partitions par mots de croissance restreinte, puis test direct de la congruence.

Résultat : **49 congruences** dans chaque méthode, avec égalité des deux ensembles de partitions.

Pour chaque quotient, les ombres ont été recalculées par énumération des colorations binaires, avec le critère V19 singleton et les égalités de trajectoire aux temps 0 et 1. La canonisation applique les rotations simultanément à tous les masques d'une ombre.

## 3. Résultats

- Congruences : **49**.
- Quotients conservant le cycle, les huit paires distinctes et la cohérence : **9**.
- Répartition par taille : 5 états : 1 ; 6 états : 2 ; 7 états : 3 ; 8 états : 2 ; 9 états : 1.
- Quotients conservant les huit classes d'ombres : **1**.
- L'unique quotient conservant les huit classes est la partition discrète, de taille **9**.

Conclusion : aucun quotient de congruence propre de ce témoin ne conserve les huit ombres exactes.

## 4. Invariance de représentation

Les cinq états hors cycle ont été renommés selon les **120** permutations possibles, en transportant T et les huit paires. Les huit classes restent identiques après canonisation par rotation du C4.

## 5. Réconciliation avec le témoin historique à 12 états

L'ancien rapport du 27 octobre établissait seulement qu'un témoin à 12 états ne se réduisait pas par congruence. Il ne donnait pas de borne globale sur toutes les dynamiques. Il ne contredit donc pas le témoin à 9 états.

## 6. Raccord primaire V19 — correction

La note primaire `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` a été retrouvée intégralement dans la bibliothèque (359 lignes) et relue le 4 novembre. L'audit du 14 octobre avait déjà documenté une lecture partielle de ses lignes 1–120.

La note primaire établit :
- section 2 : critère exact des contraintes singleton, `T(u)=T(v)` ou `{T(u),T(v)}={u,v}` ;
- section 3 : structure P1–P4 du graphe forcé cohérent ;
- section 4 : mauvais événement par égalités aux temps `0≤t<L` et théorème de petit modèle jusqu'à `L+2`.

Pour L=2, les égalités sont exactement aux temps 0 et 1 et le préfixe local s'étend jusqu'à t=4. Le vérificateur local indépendant construit ce préfixe ; les deux vérificateurs globaux calculent directement sur tous les états. Le raccord sémantique est donc fermé pour C4, L=2. Voir `RACCORD_PRIMAIRE_V19_C4_L2_2026-11-04.md`.

Correction : l'ancienne version de ce rapport indiquait à tort que V19(2) n'avait pas été récupérée. Elle était présente dans la bibliothèque ; l'audit antérieur du 14 octobre l'avait partiellement consultée.

## 7. Verdict RAVI-2

- Quotients congruents du témoin : **CALCUL EXACT**.
- Absence de quotient propre conservant les huit ombres : **CALCUL EXACT**.
- Invariance sous 120 renommages transitoires : **CALCUL EXACT**.
- Minimalité globale N=9 : **CALCUL EXACT** sous la définition primaire V19(2), pour le catalogue C4O-00…07.
- Originalité bibliographique : **INDÉTERMINÉE**.
- Certification Lean : **NON RÉALISÉE**.

## 8. Reproductibilité et provenance

Script ajouté : `code/audit_quotients_temoins9.py`.

Les algorithmes de génération des congruences et de vérification des ombres ont été réimplémentés et exécutés dans une session Python séparée. Le fichier GitHub a été récupéré et inspecté ; ne pas affirmer qu'il a été exécuté tel quel. Sorties :
```
CONGRUENCES 49
CYCLE_AND_PAIR_VALID_COHERENT 9 sizes {5: 1, 6: 2, 7: 3, 8: 2, 9: 1}
PRESERVE_ALL_TARGETS 1
TRANSIENT_RELABELINGS_TESTED 120 all_eight_target_classes_invariant True
```

Aucune modification de `main` ni fusion de PR.
