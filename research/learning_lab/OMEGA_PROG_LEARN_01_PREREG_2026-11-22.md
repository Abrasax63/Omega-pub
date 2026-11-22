# OMEGA-PROG-LEARN-01 — expérience PRÉENREGISTRÉE avant le modèle

**22 novembre 2026. Statut : protocole pré-enregistré ; résultats non connus.**

## Décision d'architecture et isolement

Le dépôt public Omega-pub n'est pas rendu privé. Cet essai **n'utilise que des
programmes jouets inventés pour l'expérience**, ne copie aucune donnée privée,
ne touche pas à main et n'écrit pas dans les poids d'Omega.

L'intention à moyen terme reste un dépôt **privé distinct**, mais ce premier
test vérifie si une boucle d'apprentissage est utile avant de bâtir davantage
d'infrastructure. La connexion GitHub actuelle ne fournit pas d'action de
création de dépôt. Ne pas présenter cette branche publique comme privée.

## Questions falsifiables

1. Un modèle local Qwen2.5-3B-Instruct Q4_K_M peut-il, sans code source,
   apprendre à reconstituer une fonction Python inconnue **A** en observant
   seulement les entrées/sorties et des retours d'erreurs de développement ?
2. Sa synthèse de l'expérience A l'aide-t-elle à reconstruire **B**, un
   programme différent, sur **36 entrées inédites identiques** à celles
   utilisées pour la version sans expérience ?
3. Les programmes produits sont-ils exécutables dans une boîte à outils
   restreinte, sans import, I/O, réseau ni accès aux tests cachés ?

Le modèle peut s'abstenir, échouer à produire du JSON, écrire du code incorrect
ou ne montrer aucun transfert. Un résultat négatif reste informatif.

## Programmes inconnus et indépendance des tests

Les deux programmes cibles sont des transformations de chaînes ASCII vers
listes de chaînes, mais leurs comportements et leurs états sont différents.
Le code oracle est conservé dans le **runner de confiance**, jamais copié
dans les messages du modèle.

- A : regroupe les répétitions adjacentes en ignorant la casse, convertit la
  lettre en minuscule et rend une représentation des segments.
- B : sépare des champs textuels avec délimiteur et caractères échappés.

Ces descriptions sont **pour l'évaluateur, jamais pour Omega**.
Le modèle voit uniquement sept exemples fixes par cible, puis peut demander
jusqu'à trois observations supplémentaires **de son choix**.

Après un premier programme candidat, il reçoit les résultats d'au maximum
quatre échecs parmi sept cas de développement déterministes et peut corriger
son code une fois. Les 36 cas cachés, générés par graine fixe et disjoints des
exemples/development, ne lui sont jamais communiqués, même après son premier
essai. Il n'y a aucune nouvelle tentative après leur notation.

## Bras comparatifs

Ordre pré-enregistré pour éviter qu'un entraînement antérieur influence
la condition de contrôle :

- **B_direct** : 3 appels (probes, premier code, correction) sur B seul.
- **A_learning** : 3 appels (probes, premier code, correction) sur A.
- **mémoire** : 1 appel libre pour formuler un enseignement général de A.
- **B_transfer** : 3 appels sur B avec cet enseignement général, mais **sans
  code source A, sans programme B, sans solution et sans copie d'oracle**.

B_direct et B_transfer ont les **mêmes sept exemples initiaux, le même ensemble
de sept cas de développement et les mêmes 36 tests cachés**, les **mêmes trois
plafonds de génération** (140 + 660 + 700 tokens). Ils peuvent choisir des
probes différentes ; le contexte de B_transfer est plus long et l'expérience
A coûte quatre appels additionnels. Ceci empêche d'attribuer un effet causal
sans autres contrôles. Nous enregistrons ces différences.

Ce pilote mesure d'abord une forme d'**apprentissage en contexte et transfert
de stratégies**, pas un entraînement neuronal. La mémoire est un résumé
textuel temporaire ; les poids du modèle restent inchangés.

## Interdiction des illusions d'auto-amélioration

- Ne pas utiliser les fonctions oracles dans les prompts, le contexte LLM ou
  le feedback de holdout ; préserver les sorties brutes et les programmes.
- Ne pas examiner une sortie cachée puis la donner au modèle et recompter ce
  second essai comme indépendant.
- Les tests cachés sont **séparés** des observations et des cas de réparation.
- Toute erreur Python est comptée comme erreur ; aucun correctif humain des
  programmes proposés n'est permis.
- Exécuter le code généré avec syntaxe restreinte : une seule fonction,
  pas d'import, I/O, introspection, appels dynamiques ; subprocessus isolé,
  environnement nettoyé, limite CPU/temps et mémoire.
- Le workflow GitHub n'utilise aucun secret, aucune écriture sur GitHub,
  aucun système local du propriétaire ; toujours runner éphémère.
- Aucun cron, aucune activation continue, aucun commit ni fusion automatique.

## Environnement et coûts

- GitHub Actions sur branche expérimentale publique, runner Ubuntu CPU.
- llama.cpp b12633, modèle Qwen2.5-3B-Instruct Q4_K_M.
- SHA-256 du modèle visé, obtenu dans le run mathématique précédent :
  9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94.
- Origine : bartowski/Qwen2.5-3B-Instruct-GGUF, GGUF Q4_K_M.
- Pas d'API payante. Maximum 10 appels du modèle dans ce protocole.
- Graine modèle 47621, température 0.
- Les journaux et les sorties brutes archivés en artefact éphémère.

## Critères de lecture

- **Logiciel** : unit tests des règles, du sandbox et des oracles réussis.
- **Reconstruction A** : score entier sur 36 cas inconnus.
- **Transfert B** : score direct vs score après mémoire, et coût total.
- **Gain démontré ?** NON sur un seul essai : le transfert peut être nul,
  dû au contexte supplémentaire ou fluctuer. Ne qualifier que d'observation.
- **Apprentissage des paramètres** : explicitement NON, même si B_transfer
  semble meilleur.

Après un run, effectuer un audit des sorties, du coût et du risque de fuite,
puis décider d'une expérience nouvelle pré-enregistrée sur un autre jeu, ou
d'abandonner la piste si le signal est nul à répétition.

## Suite conditionnelle

Si la reconstruction devient fiable, étendre la bibliothèque de compétences
logicielle, introduire des tâches inconnues plus éloignées, puis **seulement**
expérimenter l'adaptation de paramètres (LoRA) et la génération de tout petits
modèles neuronaux. Un score nul n'autorise pas à faire comme si Omega avait
appris. Aucun dépôt privé n'a été créé dans cette PR.
