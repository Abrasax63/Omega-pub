# P5-VALUE-01 — première plus-value mesurable : résultat et audit indépendant des revendications

**12 novembre 2026 — statut : EXÉCUTION RÉELLE COMPLÈTE / QUALITÉ EXPLORATOIRE / AVANTAGE PROPRE À OMEGA NON DÉMONTRÉ.**

## Preuves et reproductibilité

- [Pré-enregistrement gelé avant création du code et avant inférence](EXPERIMENT_P5_FIRST_VALUE_PREREG_2026-11-12.md) : commit `5c1e8f11e61bc44ecf05d5c7a378fcfdd1daac71`.
- [GitHub Actions run 43183956200](https://github.com/Abrasax63/Omega-pub/actions/runs/43183956200) : **SUCCESS**, 6 tests hors fournisseur réussis, **54 générations de modèle réellement effectuées**, 0 appel API OpenAI, aucun calcul smartphone.
- [Archive brute des 54 réponses et mesures](https://github.com/Abrasax63/Omega-pub/actions/runs/43183956200/artifacts/13928490263) : données publiques, conservation GitHub 3 jours.
- Modèle : `Qwen/Qwen2.5-0.5B-Instruct`, révision explicite `7ae557604adf67be50417f59c2c2f167def9a775`; 18 cas publics nouveaux × A/B/C, une répétition, `max_new_tokens=96`.
- Empreinte SHA-256 des cas publics : `2f47fbb2656237a0ca7d28e54ba6401c962a2175191edafc520d08e02ff5acf0`.
- Aucun corpus ni corrigé privé P5 v0.5 n'a été consulté ou publié.

## Comparaison du petit modèle (18 cas chacun)

| Indicateur | A directe | B perspectives fixes | C Omega adaptatif |
|---|---:|---:|---:|
| Exactes **et** récupérées automatiquement | 3/18 | 4/18 | 5/18 |
| Sorties sans réponse parsée | 6/18 | 6/18 | 5/18 |
| Tokens d'entrée | 5 030 | 7 478 | 6 056 |
| Tokens de sortie | 1 149 | 1 608 | 1 630 |
| Durée cumulée de génération | 141,544 s | 202,979 s | 197,594 s |

**Le score automatique n'est pas une note sémantique indépendante.** Le modèle a parfois suivi littéralement l'instruction `Réponse: VALEUR` en générant « VALEUR », puis a exprimé une bonne incertitude dans le texte. Exemple `VALUE-DOC-04` : A écrit « La réponse est INDETERMINE » mais la phrase n'était pas au début de la ligne et son extraction a échoué ; C exprimait la même conclusion avec une forme reconnue. **La différence de score DOC ne doit pas être présentée comme un avantage de raisonnement.**

Détail des scores stricts par catégorie :

| Domaine | A | B | C |
|---|---:|---:|---:|
| Congruences CRT (6) | 0 | 1 | 1 |
| Taux agrégés (6) | 3 | 3 | 3 |
| Documents non authentifiés (6) | 0 | 0 | 1 |

Sur les six cas de taux, **les trois approches produisent les mêmes réponses**. Sur les congruences, C et B réussissent seulement `CRT-02`, A échoue. L'écart C–B sur cette grille vient donc uniquement du parseur documentaire. Les résultats ne démontrent aucune supériorité stable du Prisme.

À titre descriptif, avec seulement deux paires discordantes en faveur de C face à A, le test binomial exact bilatéral sous hypothèse d'égalité donne `p=0,5` ; face à B, une seule paire discordante donne `p=1`. Ces valeurs **ne certifient ni équivalence ni absence d'effet** ; puissance statistique très faible et notation imparfaite.

## Valeur du vérificateur vs valeur propre d'Omega

| Condition | Verdicts attendus / 18 | Appels de modèle | Appels au vérificateur |
|---|---:|---:|---:|
| A + outil exact | 18 | 18 | 12 |
| C + même outil exact | 18 | 18 | 12 |
| Vérifier systématiquement (V-all) | 18 | 0 | 18 |
| Omega-route sans modèle | 18 | 0 | 12 |
| Type-route sans modèle | 18 | 0 | 12 |

Les 12 tâches calculables ont un **oracle exact** (CRT : brute force pour la référence, inverse modulaire pour le vérificateur ; DATA : `Fraction` vs produits croisés). Les 6 documents ne peuvent être authentifiés avec les données disponibles : l'abstention `INDETERMINE` est la réponse attendue et imposée par politique. Ces **18/18 sont des vérifications de cohérence et de routage sur tâches construites**, pas une nouvelle performance de modèle ni une réussite statistique d'Omega.

**Contrôle falsifiant : Omega-route = Type-route, exactement 18/18 et 12 appels pour les deux.** La politique adaptative en place n'apporte aucune plus-value spécifique observable face à une simple règle `mission_type == computational` sur cet ensemble. L'économie de 6 appels par rapport à V-all est réelle au niveau du compteur logiciel, mais n'est pas unique à Omega.

**A+V = C+V = 18/18**, donc le gain des réponses corrigées est entièrement compatible avec la valeur intrinsèque du calculateur disponible aux deux approches. Il n'est pas légitime de l'attribuer à la stratégie C.

## Conclusions scientifiques

- **DÉMONTRÉ pour ce pilote** : exécution de 54 générations distantes gratuites sans OpenAI API ; vérificateur exact cohérent avec deux implémentations indépendantes ; journaux archivés ; A/B/C reçoivent des données communes ; contrôle négatif Type-route effectivement appliqué.
- **OBSERVÉ, non généralisable** : C=5/18, B=4/18, A=3/18 sur une métrique composite sensible à la forme ; C n'est pas plus économe en tokens ou latence que A dans ce test.
- **NON DÉMONTRÉ** : avantage propre à Omega en qualité sémantique, meilleur choix de vérification que des heuristiques simples, transfert à un grand modèle, robustesse à des tâches inconnues et nouvelles.
- **Limitations** : cas publics conçus par l'auteur, sans double aveugle, une répétition, petit modèle 0,5B, parser sensible aux formulations et emplacements, documents simulés, résultat `INDETERMINE` artificiellement attendu pour tous les cas documentaires.
- **Prochain verrou** : pré-enregistrer des tâches nécessitant des décisions de vérification *non réductibles* au champ `mission_type`, avec **même outil accessible au contrôle naïf**, coûts de vérification hétérogènes, et plusieurs modèles/itérations. Ne pas « améliorer » le parseur de ce jeu après lecture des réponses en prétendant conserver un holdout.

Ce rapport est un **audit falsifiable**, pas une promesse de plus-value. La PR #49 reste en draft ; `main`, PR #47/#48, les fichiers et engagements privés ne sont pas modifiés.
