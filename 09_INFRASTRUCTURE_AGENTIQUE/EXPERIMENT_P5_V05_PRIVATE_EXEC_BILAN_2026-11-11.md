# P5 v0.5 — résultats du préflight privé et décision scientifique

**11 novembre 2026 — statut : PREFLIGHT VALIDÉ / 0 APPEL MODÈLE RÉEL / AUCUNE NOTATION INDÉPENDANTE.**

## Source figée avant exécuteur

- [Manifeste public v0.5](evaluation/p5_v05_candidate_public_manifest.json), gelé au commit `ce9a5818928e05d8ec0d1330d5f27a00b732149d` avant création du runner.
- 16 nouvelles questions candidates : formalisation, CRT, documents synthétiques, taux stratifiés. Les contenus et les corrigés **ne sont pas dans le dépôt public**, mais conservés séparément dans la bibliothèque privée `/Omega-Private/P5V05-Candidate-2026-11-11`.
- SHA-256 entrée et corrigé comparés de nouveau aux deux fichiers privés par une exécution locale distincte : **concordance stricte**, 16 identifiants alignés, 0 réponse divulguée.
- Les fichiers locaux temporaires ont des permissions `0600` et le répertoire `0700`. La Bibliothèque privée impose ses propres règles d'accès, distinctes de ces permissions POSIX.

## Preuve de fonctionnement de l'exécuteur : pas d'appel réel

- [GitHub Actions #43105698649](https://github.com/Abrasax63/Omega-pub/actions/runs/43105698649) : **SUCCESS**, 20 tests Python — sécurité des prompts, parité A/B/C, source hachée, refus des champs de vérité, ordre des répétitions, contrôle des tokens, contrôle anti-rejeu, et 96 réponses produites par un **fournisseur factice explicitement simulé**.
- [Tests RCE #43105698527](https://github.com/Abrasax63/Omega-pub/actions/runs/43105698527) : **SUCCESS**.
- Le module `prism/p5_v05_private_runner.py` n'importe jamais un corrigé ni une graine privée de la Bibliothèque. Les 96 requêtes sont soumises à un **précomptage** de tokens ; en cas de plafond insuffisant, 0 génération. `--execute --allow-billable-api` et le nombre exact d'appels approuvés sont requis. Les réponses réelles, si elles sont un jour obtenues, sont conservées hors Git via le `DispatchLedger` déjà existant.
- Le workflow CI `.github/workflows/omega-p5-v05-private-runner.yml` n'a **aucune clé API, aucune question secrète et aucun fournisseur payant**. L'API de génération n'a pas été utilisée ici.

## Audit de qualité du nouveau corpus — limite détectée avant modèle

L'audit local du corrigé, hors Git et avant appels de modèle, détecte un défaut de **diversité des verdicts dans la sous-partie FORMAL**. Ce segment de quatre cas risque donc de mesurer la connaissance d'une régularité triviale plutôt que la capacité de réfutation adaptative. Il serait scientifiquement trompeur de le traiter comme un holdout robuste.

**Décision :** garder les engagements v0.5 inchangés, avec leur historique, mais classer ce corpus comme **candidate calibration / petit pilote interne uniquement**. Pour l'évaluation réellement décisive, utiliser une cohorte v0.6 conçue indépendamment, couvrant les cas positifs/négatifs/indéterminés, validée et gelée avant l'appel du modèle. Aucune amélioration des prompts n'est autorisée à partir des futurs résultats de v0.5.

## Vérification de capacité d'appel externe

Le conteneur de calcul ne contient **aucune** variable `OPENAI_API_KEY`, `VERCEL_AI_GATEWAY_API_KEY` ou `ANTHROPIC_API_KEY` disponible. La session ne possède pas une interface autorisée et déjà authentifiée pour émettre 96 générations de manière isolée. Le parcours sécurisé de configuration de clé API OpenAI a été ouvert **sans afficher de secret dans la conversation** et attend l'action explicite de l'utilisateur. Une souscription ChatGPT ne remplace pas un accès payant à l'API.

**Tant que ce verrou n'est pas levé, il est inexact de dire que le benchmark A/B/C a été exécuté.**

## Plan strict de continuation

1. Audit externe d'une nouvelle cohorte v0.6 secrète, indépendante du concepteur, avec corrigés privés et empreintes antérieures aux tests ;
2. choix d'un unique snapshot de modèle et d'un budget réel de tokens/appels ou de dépense, constatation de la disponibilité API via un client authentifié ;
3. 96 générations (ou autre population pré-enregistrée v0.6) isolées, traces exactes de tokens/appels et refus des envois multiples incertains ;
4. évaluation double aveugle et comparaison appariée C−B, C−A, B−A, avec erreurs confiantes et abstentions ; publier les limites et les échecs.

PR DRAFT uniquement ; main, CORE, SQLite et travaux Lean inchangés. **Aucun avantage causal d'Omega n'est encore démontré.**
