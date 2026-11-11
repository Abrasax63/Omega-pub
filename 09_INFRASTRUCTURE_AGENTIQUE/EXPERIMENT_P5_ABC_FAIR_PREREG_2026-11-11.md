# OMEGA-P5-ABC-001 — benchmark A/B/C équitable, pré-enregistrement avant génération

**11 novembre 2026. Gel de conception AVANT nouveau générateur et avant tout résultat de modèle.** Branche `experiment/p5-abc-fairness-benchmark-2026-11-11`, indépendante des PR Lean #44 et PROBE #45, dérivée de la PR #31.

## Question

À modèle, documentation, sources visibles, plafond de génération et accès aux outils identiques, le **routage adaptatif réel du Prisme** `plan_mission` améliore-t-il les réponses au-delà d'une réponse directe ou de perspectives fixes ?

Comparer **A — direct**, **B — cinq perspectives fixes**, **C — perspectives choisies par le vrai `plan_mission`**. Les rôles sont des **perspectives du même modèle**, pas cinq agents indépendants. Les comparaisons principales sont `C−B` (effet marginal du routage) et `C−A` (effet de la décomposition complète), et `B−A`. Hypothèse nulle : aucun gain.

## Sources et statut de divulgation

La source de calibration existante est **publique**, [PR #30](https://github.com/Abrasax63/Omega-pub/pull/30), fichier `09_INFRASTRUCTURE_AGENTIQUE/prism/p5_multidomain_public_cases_2026-11-11.json` dans le parent #31, blob Git `3eb87dc5b8851dd30c753cb54e0d03659c62441b`. Elle comprend **24 questions** (6 GitHub, 6 HTTP/RFC 9110, 6 URI/RFC 3986, 6 Python), 8 manipulations artificielles de l'observation primaire et 8 notes secondaires factuellement fausses. Tout cela est **connu publiquement** et n'est pas un holdout.

Chaque observation primaire figurant dans un prompt est une **affirmation de source simulée, non authentifiée**, y compris quand elle correspond à la vérité de référence. Le cas de source inversée n'est pas présenté comme une altération réelle du site officiel, et le bras modèle n'est pas informé du marquage « inversé ». Les trois bras ont **exactement** la même représentation de la question, du domaine, de la référence et des deux observations (référence primaire simulée / note secondaire fictive). Le seul champ de différence est l'instruction de stratégie A/B/C. Un lien officiel ne constitue pas un document consulté lorsque les outils sont interdits.

**AUCUN résultat sur ce paquet public ne pourra prétendre être aveugle, indépendant du concepteur ou représentatif.** Les 24 cas sont du matériel de calibration de l'infrastructure A/B/C et de détection de faux positifs, pas un test validant l'intelligence scientifique d'Omega.

## Verrous expérimentaux

1. Corriger le **défaut déjà observé** dans `p5_four_arm_protocol.py` : C y recevait un **contexte structuré supplémentaire**, qui avantage illégitimement C. Le nouvel adaptateur n'utilisera PAS ce constructeur, et ne modifiera pas l'ancien ; il refusera toute clé de vérité, note de correction ou métadonnée cachée.
2. Déterminer la `mission_type` depuis une règle fixée **uniquement sur le domaine public** : `github/http -> documentary`, `uri/python -> computational`. Cette règle et le domaine sont affichés dans le tronc commun des trois bras. Aucune déduction oraculaire du verdict.
3. `plan_mission` est appelé avec uniquement question et mission_type, en utilisant la version du parent. Pas de contexte décisionnel externe, pas de mémoire privée ni de provenance préstructurée donnée à C.
4. **Budget de génération identique** : même identifiant/snapshot de modèle, instructions, limite de sortie, plafond total des tokens et `tools=[]`, `store=false`, pas de retries silencieux. Le nombre de tokens d'entrée **réel** devra être mesuré avant chaque appel (et inclus dans le plafond total) ; **ne pas utiliser la longueur en caractères comme prétendue mesure de tokens**. Si le SDK ou le fournisseur ne fournit pas les métriques nécessaires, marquer `NOT_RUN`/budget indéterminé, ne pas créer un score comparable.
5. Deux répétitions isolées par cas/bras et condition, avec ordre des bras randomisé à partir d'une graine figée **avant le lancement réel**. **Aucune graine publique ne constitue un aveuglement véritable** ; les noms de bras doivent être masqués à des correcteurs indépendants.
6. Pré-enregistrer une correction sur la base des références primaires (et la portée des liens simulés), conserver les corrigés et évaluations **hors des prompts**. Deux évaluateurs indépendants et aveugles, jugement dimensionnel 0–4 : exactitude, réfutation, calibration/abstention, sources, traçabilité, erreurs confiantes ; aucun score composite ajouté après coup.
7. **Blocage des conclusions** : sans appels réels indépendants du même modèle et sans double notation indépendante, statut `PREFLIGHT_ONLY / P5_LIVE_NOT_RUN`; les assertions « Omega gagne/perd en qualité de réponse » sont interdites.

## Préflight reproductible à exécuter maintenant

- Produire **144 demandes** `24 cas × 2 conditions (source intacte/inversée) × 3 bras`, toutes sans clés de vérité dans le corps de texte.
- Auditer pour chaque groupe `case_id,condition` l'égalité **octet pour octet** du tronc commun et des instructions, aucune preuve de vérité hors documents, absence de contexte privilégié C, et l'utilisation effective de `plan_mission`.
- Vérifier la traçabilité de chaque référence et les identifiants de hachage, sans dévoiler les clés de correction dans les prompts ; les sources restent **simulées** dans cette calibration.
- Exécuter des contre-tests (injection de verdict, label d'attaque, modification du tronc commun du seul C, note de source cachée, mauvais type de mission, modification du blob/échantillon).
- Publier le paquet **prompts-seulement**, les empreintes et le verdict du préflight en CI, en indiquant explicitement : **0 appels LLM, 0 résultats notés, 0 évaluateurs indépendants, aucun gain causal mesuré**.

## Étape suivante pour la campagne réellement probante

Le holdout v0.4 de PR #10 est **public** et ne pourra pas être utilisé comme holdout aveugle. Il faut une **nouvelle cohorte privée v0.5**, des corrigés privés ayant subi un audit anti-fuite et un engagement SHA-256, une validation de provenance des sources et des budgets d'API, une randomisation privée et des correcteurs réellement indépendants. La version exécutable doit consommer ces cas depuis un stockage privé, **sans les publier sur GitHub**.

Ne pas lancer un modèle non disponible, ne pas inventer la connexion d'un fournisseur, ne pas simuler une sortie pour prétendre avoir exécuté GPT-6, et ne pas publier les sorties/jugements d'un holdout privé.

## Règle d'arrêt

Tout cas avec information asymétrique, corrigé visible par un bras, métadonnées absentes, fuite d'identité du bras ou coût non comparable bloque une revendication C−B ; les sorties restent exploitées uniquement comme audit ou calibration étiqueté.

Aucun merge `main`, aucun changement de CORE/SQLite, pas de modification de #44/#45. Toute nouvelle branche benchmark doit être évaluée sous le statut qui lui revient.
