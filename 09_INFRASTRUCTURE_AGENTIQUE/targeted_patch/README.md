# OMEGA-TARGETED-PATCH-01 : réparer une seule ligne à partir d'un contre-exemple

**Statut : expérience DRAFT, sans auto-fusion ni modification de `main`.** Voir [PREREG_2026-11-15.md](PREREG_2026-11-15.md) pour le protocole fixé **avant** création du moteur et inférence.

## Pourquoi ne plus régénérer toute la fonction ?

Dans la [PR #100](https://github.com/Abrasax63/Omega-pub/pull/100), quatre inférences Qwen ont reproduit exactement le même code erroné. Ce pilote exige qu'un modèle propose **une seule expression** pour remplacer la ligne conditionnelle défectueuse. Le code source historique est figé à l'octet près : SHA-256 `15fe02b6d5ea993ecb2a64eac02823345a58b631264a8eee081e70a5f3e89314`.

L'emplacement de l'erreur a été **identifié par les expérimentateurs** : le modèle ne le découvre pas librement. Le modèle doit choisir l'expression qui constitue un patch; le moteur ne lui substitue jamais la solution correcte lorsque sa sortie échoue.

## Les deux entrées comparées

- `controle_patch` : programme erroné, même contre-exemple public, document RCE de gouvernance sans rapport avec la composition.
- `memoire_patch` : programme erroné et même contre-exemple, **invariant mathématique structuré** issu d'une traduction déterministe de la fiche RCE `ALGORITHMIC_PILOT.md`. La fiche est recherchée et sa SHA de contenu vérifiée avant emploi. Les deux notes sont égales en **caractères**, pas nécessairement en tokens.

Une proposition par bras, Qwen2.5-Coder-3B Q4_K_M, modèle, binaire, température et plafond de tokens identiques. Chaque sortie est enregistrée et transformée en patch seulement si elle est une expression Python AST autorisée et qu'elle modifie **exactement la ligne 11**. Le code amendé ne s'exécute que dans le sandbox Docker sans réseau.

## Références et critères

Quatre micro-cas publics et trois familles de développement testent d'abord l'exactitude de `Q^h` et de `\Delta_h`. Seuls les candidats corrects ouvrent **une fois** les cinq graines nouvelles, tirées et gelées par empreinte SHA-256 **avant** la première inférence. Deux références classiques fortes sont exécutées sur la même réserve : `square-scan` et `square-lowbit`. Une source connue, un patch sans changement ou une source identique entre les deux bras ne peut être revendiquée comme un gain d'intelligence. Le gate ne peut proposer au mieux qu'une **revue**, à marge de coût supérieure à 15 %, jamais une promotion automatique.

Le rapport archive plan P1, contexte P2, provenance RCE, programmes source avant/après, sorties Qwen brutes (queue bornée + empreinte), expression proposée, tests exacts, coûts, scores, décisions et journal P3 de six événements.

## Exécution

```bash
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/targeted_patch -p test_targeted_patch.py -v
python 09_INFRASTRUCTURE_AGENTIQUE/targeted_patch/targeted_patch.py \
  --llama-cli /chemin/llama-cli --model-file /chemin/qwen.gguf \
  --output targeted-patch-result.json
```

Le [workflow de GitHub Actions](../../.github/workflows/omega-targeted-patch.yml) lance d'abord les tests sans modèle, puis **deux** inférences Qwen réelles avec poids vérifiés et sandbox, et archive le JSON.

## Limites

Une seule paire de propositions, un bug et un emplacement connus, un compilateur d'invariant déterministe et interne, notes égalisées en caractères et non en tokens, cinq cas réservés créés dans le même job et temps Docker bruités. Un patch mathématiquement correct peut être une **capacité locale de réparation**, pas une nouvelle théorie, un nouveau programme optimal ou une amélioration cognitive générale. Le RCE n'est pas un prouveur général ni un oracle bibliographique indépendant.
