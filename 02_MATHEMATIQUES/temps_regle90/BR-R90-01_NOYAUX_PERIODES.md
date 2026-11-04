# BR-R90-01 — Noyaux et période récurrente de Règle 90

- **Identifiant source :** BR-R90-01
- **Version publiée :** 0.1 (transfert documentaire)
- **Domaine :** Mathématiques / dynamique linéaire sur corps fini
- **Statut scientifique enregistré dans la fiche source :** DÉMONTRÉ
- **Statut de publication :** EXPÉRIMENTAL — preuve détaillée et audit source non encore joints à ce dépôt
- **Source documentaire :** bibliothèque de recherche interne, fiche `BR-R90-01_NOYAUX_PERIODES.md`
- **Audit source cité par la fiche :** `/Recherche/02_PROGRAMMES_ACTIFS/Temps_Regle90/AUDIT_TEMPS_REGLE90_2026-08-22.md`, sections 2 et 4

## 1. Domaine

Règle 90 sur un cycle de taille (N), vue sur (mathbb F_2) par l'opérateur
(A_N=z+z^{-1}). Écrire (N=2^a m), avec (m) impair.

## 2. Énoncé 1 — noyau transitoire

Pour tout entier (t\geq 0),

[
\dim\ker(A_N^t)=\min(2t,2^a)
]

et

[
\operatorname{rang}(A_N^t)=N-\min(2t,2^a).
]

La composante récurrente a donc dimension (N-2^a).

Cas particulier : pour (N=2^a),

[
A_N^{2^{a-1}}=0.
]

## 3. Énoncé 2 — période maximale récurrente

Pour (m>1), si (L_m) désigne l'ordre de (z+z^{-1}) sur la composante récurrente impaire, alors

[
L_N=2^a L_m.
]

La convention de l'audit prend (L_{2^a}=1) lorsque la composante récurrente est nulle.

## 4. Limites

La formule concerne la période maximale de la composante récurrente, pas la période de chaque état ni celle d'une observation particulière.

## 5. Éléments de preuve et vérification disponibles

La fiche source renvoie à l'audit indiqué ci-dessus, mais le texte intégral de cet audit n'a pas encore été transféré dans le dépôt public. Une comparaison documentaire datée du 14 octobre 2026 rapporte un contrôle exact sur (N=2,\ldots,12), cohérent avec les formules, mais ce contrôle fini ne remplace pas la preuve générale.

**Conséquence éditoriale :** le statut scientifique DÉMONTRÉ est celui porté par la fiche source interne. Le statut de publication reste EXPÉRIMENTAL tant que la preuve détaillée, ses hypothèses complètes et le protocole de reproduction ne sont pas disponibles publiquement.

## 6. Dépendances

Aucune dépendance formelle n'est déclarée dans la fiche source transférée.

## 7. Historique

- 0.1 — Transfert fidèle de la fiche source vers Omega-pub ; aucune nouvelle preuve ni exécution n'est revendiquée.
