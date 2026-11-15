# OBS-COL-05 — Pré-enregistrement avant code et résultat
Date : 2026-11-15. Base : PR #87 ; branche : `experiment/obs-col05-representation-expansion-2026-11-15`.
Statut : hypothèse expérimentale, NON EXÉCUTÉE au moment de cet engagement.

## Question
Un dispositif expérimental utilisant le vrai planificateur Omega P1 peut-il détecter l'insuffisance d'une représentation affine GF(2) d'un système fini inconnu, développer une représentation non linéaire à partir de transitions observées et signaler un modèle hors famille lors de contrôles séparés ?

## Ensemble fini, mesures et fuites
5 bits, 32 états, deux actions `pulse` et `bind`. Les transitions exactes de quatre systèmes synthétiques sont codées par **un oracle caché au module d'inférence**, même si les formules sont publiques aux auditeurs.
Les systèmes sont gelés ici avant l'implémentation :
- A (affine) : `pulse: x ^ 4 ^ (b1<<3)` ; `bind: x ^ 16 ^ b4`
- Q (quadratique) : `pulse: x ^ ((b0&b1)<<4) ^ (b2<<1)` ; `bind: x ^ ((b1&b3)<<2) ^ b4`
- C (cubique) : `pulse: x ^ ((b0&b1)<<4) ^ (b1&b2&b3)` ; `bind: x ^ ((b1&b3)<<2) ^ ((b0&b2&b4)<<1) ^ 8`
- OOD (quartique) : mêmes actions que Q, sauf `pulse` modifié par `((b0&b1&b2&b3)<<4)`.

Les bits `b_i=(x>>i)&1`. Ces mondes sont construits à la main ; **pas de holdout aveugle externe ni de données naturelles**. Tous les bits de sortie sont observables via une intervention dans le simulateur. Le monde réel n'est **jamais** passé en argument à la régression ni au planificateur.

## Protocole
- Pour chaque action, interroger 26 états de départ (sous-ensembles de bits de poids <=3) choisis sur la base de l'indépendance des vecteurs de monômes GF(2) de degré <=3. Le planificateur P1 doit recevoir à chaque étape une requête de vérification ; P1 n'est **pas** crédité d'avoir inventé la sonde si le sélecteur matriciel la détermine.
- Démarrer par une représentation affine de degré <=1. En cas d'incompatibilité exacte avec les observations, envisager le degré <=2, puis <=3. Si aucun modèle de degré <=3 ne convient, signaler une anomalie sans forcer d'explication.
- Réserver les 6 états de poids >=4 **par action** à l'évaluation ; ne pas les utiliser pour choisir le degré ou ajuster les coefficients. Évaluer séparément chaque action.
- Après ajustement, tester les prédictions sur toutes les 12 transitions réservées. Une erreur -> `OUT_OF_FAMILY_WARNING`, aucune promotion de certitude.
- Comparateurs : affine fixe sur mêmes observations ; polynomial de degré <=3 fixe sur **les mêmes 52 observations** (baseline forte), plus un oracle d'évaluation indépendant sur les 12 transitions réservées. Aucun gain revendiqué sur la baseline polynomiale.
- Mesures : promotions de degré, exactitude sur le holdout, faux certificats, mises en garde OOD, erreurs, nombre de requêtes, appels P1, nombre d'appels modèle, hyperarêtes effectives de variation d'états.

## Décision pré-enregistrée
Succès technique si les quatre mondes passent les tests de protocole et que Q/C déclenchent respectivement les promotions attendues ; OOD doit déclencher un avertissement si les mesures réservées l'exposent. En cas de test manquant, FAIL et pas de revendication de capacité Omega.
Succès scientifique **non établi** même si tout passe : l'algèbre GF(2), la recherche de base et le seuil de degré sont fournis par le concepteur. Pas de nouvelle loi universelle, pas d'autonomie ni d'amélioration d'intelligence démontrée.
