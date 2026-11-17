# OMEGA-NATURAL-QUERY-08 — lecture prudente de questions françaises

**Statut : expérimental / PR DRAFT #155.** Ne pas confondre traduction d'une grammaire contrôlée et compréhension générale de la langue ou des mathématiques. Sans API payante, sans entraînement de poids, sans fusion dans `main`.

## Pipeline effectif

1. Reçoit une **question française** (`--text` ou fichier JSON `--query`).
2. Reconnaît quelques constructions grammaticales strictes de déduction avec des atomes entre accents graves, ou des inventaires numériques de témoins pouvant être sélectionnés indépendamment.
3. Cherche automatiquement la source dans un **catalogue de fichiers Markdown épinglés par empreinte Git**, par ses conclusions pour Horn ou par sa formule et ses conditions mathématiques pour la capacité. Le programme ne choisit pas au hasard entre deux fiches plausibles.
4. Produit une représentation typée et l'envoie au moteur `source_to_proof07.pipeline.answer` de PR #153. Vérificateurs distincts par table de vérité ou énumération exhaustive.
5. Conserve les références de source, lignes de preuve, statuts, motifs de refus et empreintes. Si la lecture ou la sélection est ambiguë, **ABSTAIN**.

## Usage sur un checkout de la branche

Depuis la racine du dépôt :

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/natural_query08/translator.py \
  --text 'Sachant `capteur` et `etalonnage`, peut-on déduire `mesure` ?'
```

Source utilisée automatiquement : `BR-LAB-CALIBRATION-08`, **règles fictives écrites pour le test**, verdict prévu `SUPPORTED` sous les deux faits cités.

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/natural_query08/translator.py \
  --text 'Nous avons 3 témoins A et 2 témoins B ; chacun est sélectionnable indépendamment. Peut-on choisir 2 A et 1 B ?'
```

Source historique `BR-OBS-CAP-03` : sélection indépendante de témoins, 2 A et 1 B réalisables dans cette instance. La réponse contient le calcul et l'audit par énumération. Le programme **ne** tranche **pas** si cette hypothèse de sélection indépendante n'est pas présente.

Pour une requête JSON `/tmp/question.json`, mettre `{"text":"<question française>","id":"essai"}` et utiliser `--query /tmp/question.json`. Les champs `gold` et `expected` sont interdits pour ce chemin utilisateur.

Rejouer le banc (résultat de développement, **non aveugle**) :

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/natural_query08/translator.py --frozen \
  --output /tmp/omega-natural-query08.json
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/natural_query08 -p 'test_translator.py'
```

## Contrôles et interprétation scientifique

- Préenregistrement avant code : commit `9e761aac`. Corpus de 20 questions et attentes avant code : `19e4849c`. Deux sources de test synthétiques nouvelles et une fiche historique inchangée.
- Le **premier run** [#44138024001](https://github.com/Abrasax63/Omega-pub/actions/runs/44138024001) a mesuré 20/20 verdicts corrects mais **19/20 attributions de source**. Le protocole a échoué, faute de reconnaissance d'une des variantes françaises (`Avec … peut-on déduire`).
- Réparation **post-hoc** au commit `85f6453`, avec contrôle spécifique supplémentaire `37deaed`. Les 20 textes et les trois sources demeurent identiques. Ne pas présenter le deuxième run comme une réplication aveugle.
- [Run final #44138224985](https://github.com/Abrasax63/Omega-pub/actions/runs/44138224985) : **15/15 tests**, 20/20 verdicts conformes, 20/20 attributions de sources, 11 réponses non-abstention, 9 refus, zéro erreur affirmée sur cette cohorte. Artefact [14354230011](https://github.com/Abrasax63/Omega-pub/actions/runs/44138224985/artifacts/14354230011).
- Référence `toujours ABSTAIN` : 9/20 réponses conformes aux attentes, **zéro** décision utile. Les chiffres ne constituent pas une estimation de performance générale : cas construits par le même auteur, grammaires connues, sources connues.

## Frontières et prochaines falsifications

- Les règles Horn sont extraites d'un format volontairement explicite; aucun synonyme scientifique libre n'est compris. Les lettres de motifs et quantités sont lues selon des constructions numériques strictes. D'autres paraphrases ordinaires doivent produire **ABSTAIN**, sans prétendre être résolues.
- Le sens mathématique général des théorèmes historiques n'est pas automatiquement reconstruit ; l'audit exact porte sur les **instances** et la forme extraite, non sur toute la science des fiches.
- Des sources concurrentes pour la même conclusion sont refusées, même si l'une semble plus pertinente : pas de sélection probabiliste cachée.
- Aucun dialogue web, connexion au modèle Qwen, mémoire autonome ou intégration au cycle horaire n'est implémenté.
- **Prochaine expérience décisive :** documents et questions réellement extérieurs au corpus de développement, plusieurs formulations libres et contrôles adversariaux, éventuel traducteur neuronal local **avec validation stricte**, mesure séparée extraction / récupération / preuve, coûts et erreurs. Préenregistrer le prochain jeu, ne pas optimiser celui de la PR #155.

**Aucune promotion ou fusion automatique.**
