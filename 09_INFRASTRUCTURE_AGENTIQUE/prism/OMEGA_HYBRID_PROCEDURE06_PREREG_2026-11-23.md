# OMEGA-PROCEDURE-06 — préenregistrement du transfert procédural

**23 novembre 2026, avant toute inférence PROCEDURE-06.**
**Statut initial : CODE + PROTOCOLE, aucune génération de ce benchmark.**
Branche expérimentale de [PR #250](https://github.com/Abrasax63/Omega-pub/pull/250). Pas d'API de modèle payante, aucun LoRA/SFT, pas de mutation de \`main\`, pas d'activation périodique.

## Question, limite causale et différence avec TRANSFER-05

[TRANSFER-05](https://github.com/Abrasax63/Omega-pub/actions/runs/45276666362) a montré que le modèle 3B peut **dire** ce qu'est la transitivité, mais que ce rappel n'améliore pas ses classifications : D = 4/8, G = 3/8, W = 3/8 (un invalide). Le critère de gain préenregistré n'a pas été atteint.

**Hypothèse plus précise :** demander au modèle un *certificat externe vérifiable* à partir des arêtes fait-il mieux qu'une réponse directe et qu'un simple rappel verbal de la règle, sur un ensemble nouveau de relations finies à cinq sommets ?

Ce test est une **intervention sur les instructions à l'inférence**, pas un apprentissage paramétrique. Même un gain ne démontrerait pas que le modèle découvre seul une méthode, ni qu'il la conserve hors contexte. L'exigence d'un certificat plus long peut au contraire pénaliser le bras procédural ; mesurer séparément classification et certificat.

## Domaine et données réservées

Univers inédit \`v0,v1,v2,v3,v4\` ; **10 arêtes non orientées possibles**, quatre boucles + les deux orientations de chaque arête sélectionnée. Les **1 024** relations de cette famille sont donc réflexives et symétriques. La seule propriété discriminante est **transitive**.

- Sélection préenregistrée \`SEED="omega-procedure06-five-nodes-preregistered-v1"\` et sélection des masques par ordre SHA-256 ; **4 positifs non triviaux, 4 négatifs**, huit classes d'isomorphisme distinctes sous les **120 permutations des sommets**.
- Aucun graphe du test précédent à 3 ou 4 sommets n'est réutilisé. Cela ne prouve pas une absence de contamination du préentraînement général du LLM, mais empêche la reprise directe de ces instances.
- Manifeste de questions \`model_inputs.json\` (ID, univers, seules arêtes). Fichier séparé \`oracle_only.json\` (vérité, toutes les propriétés fausses, éventuel témoin). Les empreintes sont calculées et archivées **avant toute inférence**.
- **Deux oracles différents** vérifient la vérité : \`check_axioms\` en énumérant les axiomes ; \`independent_clique_check\` en vérifiant que chaque composante connexe est une clique complète. Accord vérifié **exhaustivement sur 1 024 cas** dans les tests hors ligne.

## Trois conditions, 24 générations maximum

Chaque cas est envoyé dans **trois contextes stateless distincts**, avec le **même Qwen2.5-3B-Instruct Q4_K_M**, seed 9123, température 0, engine \`llama.cpp b12633\` local CPU. Les six permutations d'ordre des bras sont alternées préalablement. Pas de feedback du holdout entre appels.

1. **D — Direct :** demander \`holds\` + \`failed_axioms\`, sans méthode supplémentaire.
2. **R — Rappel verbal :** redonner la règle des triples pour la transitivité, puis demander les **mêmes** champs que D, sans preuve requise.
3. **P — Procédure avec certificat :** si \`holds=true\`, produire une **partition des cinq sommets** en blocs telle que la relation soit *exactement* l'union des paires dirigées complètes de chaque bloc ; si \`holds=false\`, donner un **triple réel** \`(x,y,z)\` où \`xRy\`, \`yRz\`, mais \`xRz\` manque. En plus, produire \`holds\` et \`failed_axioms\`.

**Contrat :** réponses JSON strictes, noms d'axiomes exacts, aucune correction de JSON, pas de témoin fourni au solveur. Le vérificateur de certificat ne fournit aucune arête ni aucun retour pendant les essais.

Pour **P**, deux scores distincts :
- \`full_axioms_correct\` : bonne classification ET liste complète des axiomes violés ;
- \`certificate_valid\` : preuve structurée mathématiquement correcte **par rapport aux arêtes réellement présentes**. Une partition valide impose l'égalité exacte des deux relations ; un témoin négatif doit vérifier chaque prémisse et l'arête manquante. Une classification correcte *sans certificat valide* n'est pas un succès procédural.

Les budgets de tokens d'entrée des trois bras sont égalisés à ±5 % avec du texte administratif neutre, et **recomptés sur la consommation réelle**. Le bras P nécessite un JSON plus long et un plafond maximal de 420 tokens comme les autres ; le **coût de sortie/temps est compté séparément**, pas artificiellement égalisé. Les effets dus à la forme/longueur de consigne restent une limitation causale explicite.

## Critère de gain fixé AVANT l'exécution

Un signal **exploratoire** de bénéfice procédural n'est signalé que si tous ces critères sont satisfaits :
- budgets de prompt comparables ±5 % avant et après appels ;
- P ≥ **6/8** pour \`full_axioms_correct\`, **ET** P ≥ **6/8** certificats vérifiés ;
- P dépasse **D et R d'au moins deux réussites de classification complète chacun** ;
- P = **0 réponse mal formée**.

Sinon \`PRE_REGISTERED_GAIN_NOT_OBSERVED\`; si tokens non comparables \`INDETERMINATE_BUDGET\`; transport / code en erreur \`TECHNICAL_FAILURE\`, sans adaptation du seuil ni ré-exécution de cette cohorte pour obtenir un verdict favorable.

L'effectif de huit cas, leurs dépendances structurelles et les interventions différentes empêchent toute conclusion statistique générale ou attribution parfaite. **Ne pas confondre** une réussite assistée par consigne avec une mise à jour de poids ou une capacité acquise durablement. Même une comparaison positive nécessiterait une réplication aveugle, différente et avec budget total comparable.

## Non-régression et sécurité

- Test logiciel du constructeur de 8 cas : non-isomorphisme exact, répartition 4+4 et absence de réponse oracle dans la requête.
- Contrôle exhaustif des deux oracles sur les **1 024** relations de l'univers.
- Rejet des certificats faux : partition incomplète ou surlarge, témoins inventés, arêtes manquantes des prémisses, JSON non conforme et propriétés mal nommées.
- Test d'exécution complet avec **faux modèle synthétique** (non compté comme expérience) : 24 appels, aucun gain revendiqué, coûts comptabilisés et résultat bloqué si budgets déséquilibrés.
- Workflow GitHub Actions **une seule fois** sur création de \`omega-hybrid-procedure06-once.yml\`, aucun cron, pas de relance automatique, ni changement de poids.
- Archive l'ensemble des questions, corrigés, réponses brutes, métriques, empreintes et versions pendant 7 jours sur GitHub ; conserver une copie durable dans le Space Omega après la vérification.

## Interprétation prochaine

Si P échoue, regarder séparément : erreur de classification malgré une consigne, ou bonne classification sans preuve ? Étudier les triples proposés, même faux. **Prochaine hypothèse** : acquisition d'une méthode algorithmique en plusieurs étapes, avec génération de tests et correction externe sur *corpus d'entraînement séparé*, puis réplication sur une nouvelle cohorte à six nœuds seulement si les coûts le permettent.

Aucune certification scientifique ou compétence neuve ne peut être promue à partir d'un seul test de prompts.