# OMEGA-PROV-002 — gel préalable : racines d'indépendance et arbitrage normatif

Date : 2026-11-11. Branche dérivée de la PR #31, sans modification de la version v0.1.
**Statut CALIBRATION PUBLIQUE NON AVEUGLE**. Il ne s'agit ni d'un test de modèles ni de nouvelles observations réseau.

## Faille ciblée
Dans `provenance_policy.py`, `_provenance_issue` valide les champs `origin`, `url`, `field`, `version` et `published`, mais ne compare pas l'étiquette `receipt["independence"]` à `check["independence"]`. Ensuite `_known_values` compte les étiquettes d'indépendance reçues. Cela permet, dans le modèle de reçus, d'obtenir artificiellement un quorum en renommant une copie.

## Expérience pré-déclarée : cinq verrouillages
1. **D5** : deux reçus de la même acquisition restent non indépendants et l'issue est abstention à deux consultations ; si l'étiquette du second reçu est remplacée par une étiquette inventée, le contrôle renforcé doit refuser cette promotion et rester abstention, à même plafond de deux consultations. Le contrôle v0.1 devrait décider indûment.
2. **T3 RFC/MDN** : la question demande explicitement *ce qu'autorise la RFC 9110*. Une table de périmètre **externe au texte observé** désigne `rule -> origin=ietf` comme autorité normative. La réponse d'un commentaire MDN ne doit pas servir de preuve normative contre le texte RFC. Budget deux, sans accès à la clé de vérité : la politique fixe et Omega doivent tous deux aboutir à `yes`, au plus deux consultations ; l'ancienne v0.1 s'abstient. **La table est un privilège d'information identique fourni aux deux stratégies**, pas une capacité autonome d'Omega.
3. **D4** : deux sources primaires également recevables et contradictoires, sans autorité pré-enregistrée ; conserver l'abstention. L'arbitrage normatif ne doit pas devenir une préférence générale pour la première source.
4. **Contenu primaire falsifié avec métadonnées exactes** : si une seule source prétendument primaire affirme `false` alors que le monde est `true`, le contrôle des métadonnées seul reste impuissant. Obtenir une fausse réponse déterminée est un **test négatif attendu**, pas un défaut à masquer.
5. **Sans effet sur les mondes et budgets** : conserver `optimize_policy` et les mondes du corpus v0.1, mêmes appels unitaires et au plus deux consultations pour B fixe et D adaptatif. Toute donnée inconnue entraîne abstention, aucune déduction depuis les champs `value` des corrigés.

## Bras
- B : ordre de consultation déterministe fixe, plus adaptateur de confiance v0.2.
- D : planificateur Omega existant avec le même adaptateur v0.2.
- Comparateur de référence v0.1 enregistré séparément, non modifié.
- Mesures : exactitude par cas, erreurs confiantes, abstentions, consultations, rejets de racine, cas d'autorité ; aucune métrique de coût réseau ni de modèle.
- Même source de données pour les deux bras, mêmes deux consultations maximum, mêmes règles de périmètre et coûts. Les scores sur le corpus v0.1 **ne constituent pas un holdout** : ils ont déjà été examinés en PR #31.

## Source normative et limites
Le texte RFC 9110 §15.4.2 autorise l'agent utilisateur à changer POST en GET pour 301. La page MDN de 308 donne une formulation incompatible à propos de 301 ; la page MDN dédiée à 301 confirme la possibilité. Le cas T3 est une contradiction de *texte public réelle*, mais ses reçus structurés sont des annotations et non des attestations cryptographiques.

- https://www.rfc-editor.org/rfc/rfc9110#section-15.4.2
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/308
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/301

## Arrêt et statuts
Exécuter les tests ciblés, les tests existants, puis rejouer avec B/D, enregistrer les écarts y compris négatifs. Sans holdout invisible et sortie de modèles isolés, aucun gain général ne peut être revendiqué. Ne pas modifier main, l'index scientifique CORE ou SQLite ; laisser la PR en brouillon.