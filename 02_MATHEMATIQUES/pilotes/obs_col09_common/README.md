# OBS-COL-09B — Consolidation du banc AALpy / LearnLib par un oracle d'équivalence commun

**Date : 2026-11-15. Statut : CALCUL EXACT / EXPÉRIMENTAL, résultats de CI reproductibles sur modèles publics.**
Base : PR #95 `experiment/obs-col09-external-aalpy-benchmark-2026-11-15`. Branche propre `experiment/obs-col09-common-eq-2026-11-15`.
Pré-enregistrement **avant code** : [PREREG.md](PREREG.md), commit `94d2233166d3a6013a94287fce2975bab41132e4`. [Amendement cache avant premier run](AMENDEMENT_CACHE_PRE_RUN.md), commit `ad230bfc23c0423ead1082b496dc28166b2a3845`.

## Ce qui a réellement été consolidé

1. Trois automates Moore **publiés par un tiers** dans [AALpy](https://github.com/DES-Lab/AALpy), leurs fichiers `.dot` d'origine et SHA de blobs inchangés. Nombre d'états : 4, 3, 9.
2. L* / KV / L# authentiques de **AALpy 2.0.0** (Python 3.11) ; TTT `TTTLearnerMoore` authentique de **LearnLib 0.18.0** (Java 17) ; L# + **véritable pont Omega P1**.
3. Le [générateur commun](generate_manifests.py) produit pour chaque modèle **512 mots de test EQ distincts** sans consulter le vrai modèle ni ses sorties (tous les mots de longueur 1 à 4, puis mots pseudo-aléatoires de longueur 5 à 18, graine `20261117 + indice`). Les deux langages reçoivent **exactement le même fichier d'entrée et la même empreinte SHA-256**, vérifiées en CI.
4. Chaque oracle d'équivalence parcourt cette liste depuis le début à chaque requête EQ, renvoie le **premier préfixe réellement contredit** ou `None` s'il n'y a aucun contre-exemple **dans cette liste bornée**. Aucun oracle parfait, pas de certification d'équivalence générale.
5. Les **256 mots d'évaluation** distincts par automate, longueurs 12 à 18, proviennent de la PR #95 ; leur manifeste est partagé et vérifié par SHA, et ils ne sont ouverts qu'après l'arrêt de l'apprentissage. Un mot de test déjà vu comme préfixe de l'apprentissage / des EQ est exclu du score « non vu ».
6. **Sans cache externe partagé**, comme précisé dans l'amendement. Les méthodes conservent leurs propres techniques internes ; la dépense réellement exécutée est comptée en resets et symboles. Plafonds : 10 000 resets et 50 000 symboles par méthode et cible.
7. L# + P1 fait appel au vrai `planner.plan_mission` avant chaque reset ; **c'est L# qui choisit toutes les expériences**, pas P1. Contrôle d'ablation : mêmes traces physiques (empreintes), mêmes resets, symboles, états appris, contre-exemples et résultats de test.

## Évidence à la tête de branche

**[CI commune #43745265582 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43745265582)** :
- **7 tests Python réussis**, 12 apprentissages AALpy exécutés, **3 apprentissages TTT Java exécutés** ;
- compilation du vrai Java TTT avec Maven réussie ;
- audit commun des empreintes EQ/évaluation Python/Java réussi ;
- [artefact unique](https://github.com/Abrasax63/Omega-pub/actions/runs/43745265582/artifacts/14174485528) : JSON complet AALpy, JSONL TTT, manifeste de **tous les mots EQ et d'évaluation**, journaux Java et rapport fusionné.

| Méthode | Resets physiques (3 modèles) | Symboles réellement exécutés | Erreurs / 757 mots réellement non vus |
|---|---:|---:|---:|
| L* (AALpy) | **1 719** | **17 967** | 0 |
| KV (AALpy) | **1 864** | **18 355** | 0 |
| L# (AALpy) | **1 636** | **17 601** | 0 |
| L# + Omega P1 | **1 636** | **17 601** | 0 |
| TTT (LearnLib) | **1 698** | **17 824** | 0 |

**Sur les trois modèles publics et pour CE protocole**, L# consomme le moins de resets et de symboles. Ce classement local ne constitue pas un résultat statistique généralisable ni une comparaison de temps CPU portable entre Java et Python.

### Détail par automate : consultations et erreurs

| Modèle | L* resets / symboles | KV | L# et L#+P1 | TTT | Évaluation non vue |
|---|---|---|---|---|---:|
| Angluin Moore (4 états) | 560 / 5 888 | 569 / 5 897 | 541 / 5 841 | 550 / 5 861 | 253/256 |
| Coffee Moore (3 états) | 519 / 5 871 | 525 / 5 877 | 519 / 5 871 | 524 / 5 881 | 250/256 |
| Moore à 9 états | 640 / 6 208 | 770 / 6 581 | 576 / 5 889 | 624 / 6 082 | 254/256 |

Les trois algorithmes Python et TTT ont le **même ensemble de séquences proposées par EQ**, mais ils n'effectuent pas obligatoirement les mêmes requêtes : les machines intermédiaires et les contre-exemples diffèrent. Par exemple sur Moore à neuf états, TTT et L# interrogent 554 mots EQ candidats, KV 622. Le banc **ne prétend pas** comparer des traces d'apprentissage identiques.

### Empreintes des trois manifestes EQ

- `Angluin_Moore.dot.eq.words` : `99405da882ebc70669b036f29d0724b04fda6ce57b1966617f6c93bdd11d444d`
- `coffee_moore.dot.eq.words` : `3b19512d34f9444ee064d1765a8f1cfbbc9460f7d71fa65cb102f334075925cf`
- `mooreModel.dot.eq.words` : `323c2e40c96fabbf593184ca2bb90b3968c32442747d43a80d04f84d9f5a33c5`

Ce sont les empreintes des octets UTF-8 avec un mot TSV par ligne. Les **mots**, non les réponses, sont figés ; les scripts de génération sont publics et indépendants des sorties des automates.

## Échec et correction de non-régression

Le [premier run #43745189728](https://github.com/Abrasax63/Omega-pub/actions/runs/43745189728) a signalé **un faux contre-exemple dans un test** : le même objet automate servait à la fois de simulateur et de candidat, provoquant une double transition. Cela ne concernait pas les entraînements réels, qui avaient un apprenant distinct. Le test a été corrigé au commit `da863352a4c9c393968af8e82bb09baa2ffc9637` en instanciant un second automate indépendant. **Tous les tests et les deux langages ont ensuite réussi.** Cet incident reste dans l'historique.

## Limites / verdict scientifique

- **VÉRIFIÉ** : véritable comparaison de plusieurs logiciels connus à oracle EQ **commun** de 512 sondes par modèle ; véritables calculs d'apprentissage, traces, coûts physiques et évaluation hors apprentissage ; absence d'effet du pont P1 sur L# et ses expériences.
- **NON PROUVÉ** : équivalence universelle (EQ borné), généralisation à d'autres automates (seulement 3 modèles tiers et publics), gain d'intelligence propre à Omega, avantage CPU de L# sur TTT (langages/environnements différents), découverte d'une loi scientifique.
- **INDÉTERMINÉ** : aptitude d'une politique Omega nouvelle à proposer des sondes plus informatives qu'une baseline forte sous contraintes et données réellement aveugles.
- Les modèles de référence sont publics et ont servi à concevoir le banc ; **pas d'évaluation externe aveugle**. Un échantillon où toutes les méthodes ont zéro erreur ne permet pas de comparer leur fiabilité sous perturbations.
- Aucune requête à un LLM, aucune auto-modification d'un agent, aucun certificat CORE.

## Reproduction

Pour des journaux **appariés**, lancer l'unique GitHub Actions `.github/workflows/obs-col09-common-eq.yml` sur cette branche ; il installe Python 3.11 + AALpy 2.0.0 + Java 17 / LearnLib TTT 0.18.0, génère le même manifeste et produit l'artefact JSON fusionné. La version antérieure PR #95 reste inchangée.

## Prochaine vérification décisive

Après cette consolidation, préparer des modèles **non utilisés dans le développement**, pris en charge par un évaluateur distinct, et une véritable politique Omega qui choisit les sondes avant de recevoir leurs réponses ; comparer coût total et qualité de généralisation à L#, KV et TTT avec un protocole commun de même manière. Préférer un verdict nul ou un échec vérifié à une amélioration supposée.

**Gouvernance :** branche de recherche en PR DRAFT empilée, pas de modification directe de `main`, de fusion ni de promotion CORE.
