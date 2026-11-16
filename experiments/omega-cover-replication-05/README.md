# OMEGA-COVER-REPLICATION-05 — réplication indépendante à budget limité

**Préenregistrement fait avant l'implémentation et toute lecture de la nouvelle cohorte :** [commit `8ba60bd`](https://github.com/Abrasax63/Omega-pub/commit/8ba60bd44553b439d109302f9a6d0a07c99e7188) ; [protocole scientifique complet](PREREG_2026-11-16.md).

Le [pilote #139](https://github.com/Abrasax63/Omega-pub/pull/139) avait donné un avantage **descriptif** à COVER_DISTINGUISH à 500 symboles (10/12 modèles exacts contre 9/12 aux trois références), mais inversé le résultat à 300 symboles. Il faut savoir si ce léger avantage se retrouve sur **d'autres machines**, sans optimiser sur les cas déjà ouverts.

## Méthodes bloquées et nouveau holdout
- **Quatre méthodes strictement inchangées** importées de #138/#139 : RANDOM_LEN10, FIXED_LEN10, OLD_OMEGA_LEN10, COVER_DISTINGUISH_LEN10. Véritable **AALpy L* 1.6.2** derrière le test d'équivalence approximatif.
- EQ **longueur exactement 10** pour chaque mot, 32 mots au maximum par modèle proposé. Chaque entrée/symbole réellement soumis au SUL est comptabilisé sur le budget MQ+EQ commun. L'accès au vrai système est interdit à l'apprenant (uniquement les requêtes et réponses), autorisé à l'évaluateur **après apprentissage**, qui vérifie l'équivalence comportementale exacte par BFS du produit.
- **48 machines entièrement inédites**, **16 à 4 états, 16 à 5, 16 à 6**, générées avec seeds 38104/38105/38106 et filtrées **uniquement** pour accessibilité et minimalité. Toutes leurs signatures canoniques sont disjointes des **1 148 machines** des PR #127–#139 et entre elles. Rejets et tentatives de génération enregistrés.
- **Budget 500** principal, **300** secondaire, **même graine pour chaque bras d'un budget à l'autre**. 128 mots réservés par machine, longueur 12–20, mêmes mots pour les 4 stratégies et les 2 plafonds. Aucun mot de test n'est utilisé pour apprendre ; les mots identiques à une requête d'entraînement sont décomptés et exclus de l'évaluation.
- **48 × 4 × 2 = 384 apprentissages AALpy** : expérience principale exécutée **une seule fois** en CI, après 10 contrôles unitaires ciblés. Historique des requêtes, réponses, hypothèses, contre-exemples, coûts, interruptions, empreintes disponibles dans l'artefact brut.

## Critère robuste, préengagé à 500

L'**unité de comparaison est la machine**, pas les 128 mots corrélés ni les requêtes. Pour chacune des trois références : W = nombre de machines exactes uniquement avec COVER ; L = uniquement avec référence. Rapporter W, L, D=W−L et D/48, ainsi que l'accuracy moyenne des 128 mots.

Le statut **`REPLICATED_STRONG_QUERY_GAIN`** exige **simultanément** face aux trois méthodes :
1. W > L ;
2. p-value du **test exact de McNemar unilatéral** corrigée par **Holm** pour 3 comparaisons ≤ 0,05 ;
3. borne inférieure d'un intervalle bootstrap apparié à 95 %, stratifié en **16/16/16 machines par taille**, strictement positive (5000 réplications, graine 48319) ;
4. aucune détérioration de l'exactitude moyenne des mots réservés (tolérance 1e-12).

Sinon `NO_ROBUST_QUERY_GAIN_DEMONSTRATED`, même si les scores moyens sont favorables. Le budget 300 constitue un **diagnostic secondaire**. Un verdict négatif ne fait pas échouer les tests techniques.

## Lancer

```sh
python -m pip install aalpy==1.6.2
python -m unittest discover -s experiments/omega-cover-replication-05 -p test_replication.py -v
python experiments/omega-cover-replication-05/replication_lab.py --output /tmp/omega-cover-replication-05.json
```

### Statut scientifique
Il s'agit d'une **réplication sur banc synthétique** de stratégies de sélection de tests pour AALpy L*, pas d'une intelligence générale démontrée ni d'un nouveau L*. Même une victoire statistique sur ce protocole nécessiterait encore validation indépendante sur d'autres générateurs ou systèmes réels. PR **DRAFT** empilée sur #139, `main` inchangée, aucune API payante, pas de fusion.
