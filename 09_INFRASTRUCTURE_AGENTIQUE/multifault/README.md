# Omega MULTIFAULT-01 — localiser des erreurs sans indiquer leur ligne

**Recherche expérimentale sur une branche distincte.** Voir le [pré-enregistrement](PREREG_2026-11-15.md) antérieur au code, aux tests et aux exécutions. `main`, CORE et les PR précédentes sont inchangés.

## Le mécanisme

Le banc génère **cinq programmes `q_power` défectueux** à partir d'une implémentation de référence connue par les expérimentateurs : quatre programmes ont chacun une faute différente (composition, XOR/OR, retour du cas h=0, borne de boucle), le cinquième a **deux fautes simultanées** comme contrôle négatif. **Le générateur `enumerate_patches(source)` ne reçoit aucune ligne fautive, aucun identifiant de défaut ni aucun corrigé** : il parcourt l'AST et propose des remplacements dans **toutes les régions compatibles avec sa grammaire**.

Ce n'est cependant **pas un benchmark externe ni une localisation générale de bogues** : les modèles de code fautif et les règles de réparation ont été écrits par les expérimentateurs et appartiennent à un domaine limité.

1. Produire jusqu'à 100 patchs de **une ligne** par programme, avec AST du programme complet vérifié, fonction et signature invariantes. Les seules modifications possibles sont les prédicats de bits, `|=`/`^=`, le cas zéro, l'initialisation de `result` et la borne de boucle.
2. Un oracle mathématique **indépendant du générateur** (`reference.walks_exact`) réfute d'abord les patchs sur trois petits tests publics volontairement faibles. Plusieurs candidats incorrects peuvent subsister.
3. Quatre décisions pour chacune des cinq tâches, avec l'**exact même groupe de candidats faiblement admis** : `symbolic_first` (premier ID), `symbolic_rce_prior` (priorité RCE humaine prédéfinie), `qwen_control` (même modèle sans note algorithme), `qwen_rce` (même modèle avec invariant RCE et texte placebo de même longueur en caractères pour le contrôle). Deux appels Qwen réels par tâche, **dix au total**, aucun code Python généré par le modèle, seulement un ID.
4. Un **cinquième comparateur fort**, `symbolic_full_public`, utilise un budget de tests publics supérieur : relations à deux états et chemins de longueur 2–4, plus plusieurs cas discriminants. Il compare la valeur du **contrôle symbolique**, mais ne constitue pas un témoin à budget égal.
5. Les programmes choisis doivent réussir l'oracle public fort, les **trois familles publiques de développement dans Docker sans réseau**, avant d'accéder à une seule réserve **nouvelle de cinq familles**. La réserve et son empreinte sont gelées **avant** la génération des candidats et les inférences ; tous les choix sont gelés à leur tour **avant** son ouverture. Les deux algorithmes classiques forts `square-scan` et `square-lowbit` servent de comparateurs. Les duplications de sources ne deviennent pas deux reproductions indépendantes.
6. Le gate d'exactitude/cost conserve les décisions `REJECTED` ou `REVIEW_REQUIRED` ; jamais publication, fusion ou promotion automatique. Le journal P3/RCE conserve empreintes, provenance des tests, propositions, contre-exemples et résultats.

### Reproduire

```sh
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/multifault -p test_multifault.py -v

python 09_INFRASTRUCTURE_AGENTIQUE/multifault/multifault.py \
  --llama-cli /chemin/llama-cli \
  --model-file /chemin/model.gguf \
  --output multifault-result.json
```

La première commande teste les composants sans modèle. La seconde exige le binaire `llama.cpp` et Qwen2.5-Coder-3B GGUF vérifiés par SHA-256 et le sandbox Docker. La [CI dédiée](../../.github/workflows/omega-multifault.yml) archive le résultat JSON des cinq tâches.

## Frontières scientifiques

L'outil apprend-il une meilleure stratégie ? **Non démontré.** Le langage AST est clos et les cas de faute sont injectés par les chercheurs. La mémoire déclenche une priorité et une note **codées en dur**, dont les effets peuvent être mesurés, sans entraîner le modèle. Les tests publics sont connus du concepteur; la réserve est créée dans le même run et non chez un évaluateur externe. Les nombres de caractères supplémentaires sont égaux, pas nécessairement les nombres de jetons. Les temps muraux Docker sont bruités et une candidate correcte peut être plus lente qu'un algorithme classique. Le benchmark ne certifie pas une nouvelle découverte mathématique.
