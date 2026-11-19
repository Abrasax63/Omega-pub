# Pilote de choix de méthode — parité et somme de sous-ensembles

19 novembre 2026 (Paris). **EXÉCUTÉ / critère confirmatoire non atteint.** Branche `experiment/omega-100-2026-11-18`, départ `23e63917d0f141441ec569a3e165c58dcb5d1112`. Pilote hors numérotation, dans le prolongement du [changement de représentation sur V19](https://github.com/Abrasax63/Omega-pub/commit/106134c049a6ca80940fab21db797fa896468bf0). Le pilote compare une décision par modèle à des politiques qui utilisent les mêmes solveurs exacts. Aucun apprentissage n'a été réalisé.

Les [conditions initiales](choice-pilot-protocol.md) fixent avant exécution les budgets, l'oracle, le témoin négatif et le seuil. Sur chaque lot, deux familles de huit cas synthétiques sont préparées en local : contraintes de parité liées à V19, et sommes de sous-ensembles positives. Les méthodes A (énumération) et B (propagation par graphe ou sommes atteignables) sont exécutées séparément avant les réponses du modèle. Au plus une méthode de 64 étapes par politique et par cas. Chaque réponse de Qwen reçoit les données et les coûts des méthodes, jamais les résultats des méthodes ou le corrigé. Le modèle sélectionne uniquement une méthode. L'étiquette provient d'une énumération exhaustive indépendante, hors budget des politiques. Un témoin positif est aussi revalidé indépendamment. Les contrôles de vérité positive, de vérité négative et d'abstention s'exécutent avant les lots. Les 16 tests métier historiques passent.

Le premier lot présentait un plafond : B réussissait déjà sur les 14 instances où au moins une méthode pouvait réussir. Il pouvait révéler une dégradation, sans marge pour un gain adaptatif. Un [second protocole](choice-pilot-cross-protocol.md) a fixé un lot distinct et renforcé A pour les sommes en essayant d'abord les valeurs seules. Le contrôle avant inférence a confirmé une marge réelle : chacune des deux méthodes réussit en exclusivité sur quatre cas par famille. Un sélecteur parfait aurait pu réussir 16/16 sur ce second lot.

| Mesure | Lot initial | Lot croisé |
| --- | ---: | ---: |
| A fixe, résultats corrects | 7/16 | 8/16 |
| B fixe, résultats corrects | 14/16 | 8/16 |
| Choix uniforme, médiane sur huit graines | 11/16 | 7,5/16 |
| Qwen, résultats corrects | 6/16 | 2/16 |
| Abstentions de la chaîne Qwen | 10 | 14 |
| Réponses erronées de la chaîne Qwen | 0 | 0 |
| Temps cumulé du sélecteur Qwen | 26,44 s | 48,01 s |
| Jetons d'entrée / de sortie | 3 998 / 128 | 4 649 / 128 |

Sur le lot croisé, Qwen choisit une méthode exploitable pour quatre cas seulement. Deux aboutissent, les deux en parité. La catégorie « aucune » des douze autres fusionne l'abstention et un éventuel échec JSON. Les seize réponses de ce lot atteignent les huit jetons de sortie alloués. Les politiques fixes font les mêmes appels aux solveurs et disposent du même plafond, mais n'ajoutent aucune inférence. Les temps solveur et sélecteur figurent séparément dans les agrégats. L'oracle de notation est hors de ces temps. Les étapes instrumentées sont des budgets algorithmiques, pas des mesures de vitesse comparables terme à terme.

## Diagnostic du format

Après ce constat, le [protocole du diagnostic](choice-pilot-diagnostic-protocol.md) a fixé un rejeu du lot croisé avec une seule lettre A, B ou N, contrainte par grammaire, et un jeton de sortie. Les instances, les solveurs et leur plafond n'ont pas changé. Les 16 réponses sont interprétables. Qwen choisit B 16 fois sur 16. Résultat : 8 correctes, 8 abstentions du solveur sur plafond, aucune erreur. La parité et la somme donnent chacune 4/8, exactement comme B fixe. Sélection : 30,41 secondes et 4 761/16 jetons d'entrée/sortie. Les 16 résolutions prennent environ 0,42 ms hors sélection dans ce rejeu. Le rejeu permet de distinguer la limite du contrat JSON du choix constant observé avec les lettres. Il ne constitue pas une validation sur de nouvelles instances.

**Décision.** Garder les politiques fixes comme références. Aucun gain de résolution ou de transfert n'est établi pour le sélecteur Qwen dans ce pilote. La sortie en une lettre est exploitable pour le prochain comparatif. Les deux lots sont petits, fabriqués pour ce diagnostic et évalués avec un seul modèle. En particulier le plafond théorique de 16/16 sur le second lot résulte d'un choix éclairé après observation des solveurs, pas d'une performance d'Omega.

## Reproduction et traces

Qwen2.5-Coder-3B-Instruct Q4_K_M local, même poids SHA-256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7` que dans [le pilote antérieur](qwen-pilot.md), llama.cpp `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`. Température 0, graine 71, un appel par choix, pas d'API payante. Lancer le même serveur que le pilote précédent sur le port correspondant (18725, 18726, 18727), huit fils, un emplacement, contexte 2048.

```sh
patch -s -o choice_cross.py choice_trial.py choice-cross.patch
patch -s -o choice_diagnostic.py choice_cross.py choice-diagnostic.patch
python choice_trial.py CAS_INITIAUX.json > initial.jsonl
python choice_cross.py CAS_CROISES.json > cross.jsonl
python choice_diagnostic.py CAS_CROISES.json > diagnostic.jsonl
python choice_score.py cross.jsonl
```

Le harnais et les deux patchs permettent de refaire le protocole avec des cas locaux JSON de type parity (n, edges) ou subset (values, target). Vérification par comparaison octet pour octet des fichiers générés par les patchs et des scripts exécutés. Cas et résultats individuels conservés hors commit. Empreintes SHA-256 des cas initiaux `1979f4a0e47c83a566d5590cb38fd39128e87b148e38d45b986305ef3e1dc2e5` et croisés `112aa6fc194eb24b5efbad3ef1c930a7084652c4e90a7f9afdf047d58d943d6f`. Empreintes des relevés individuels : initial `bc8abbc781d28c4cad0d4b73b9f6ba4824b9047f4aa6f03dca46830890595558`, croisé `615dfc0d91da31c2740a37691e42dff2526c1037798cf2cc8f79add73a4441b9`, diagnostic `5244936ff1c1b69f0c100e70081b5a33c16fee58e787432ea18ef2f26ac3766a`. Agrégats : [initial](choice-pilot-initial.json), [croisé](choice-pilot-cross.json), [diagnostic](choice-pilot-diagnostic.json).

Prochain test : une règle de sélection peu coûteuse basée sur la structure et estimée sur un corpus de développement seul. La comparer à une lettre choisie par Qwen et à B fixe sur des familles de réserve distinctes, notamment des instances pour lesquelles une estimation simple se trompe. Un gain doit être observé après facturation du temps de choix.
