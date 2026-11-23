# OMEGA-SELF-TEACH-01 — apprentissage autonome : première boucle bornée

Cette expérience réutilise le client Qwen2.5-3B et le sandbox Python de la PR #232 ainsi que les principes de conservation/rollback des PR #234/#235. Aucun entraînement LoRA n'est lancé. Le modèle n'écrit jamais dans Git et n'accède jamais aux tests cachés pendant la génération.

**Protocole figé avant l'inférence** : [PREREG.md](PREREG.md) et trois jeux de données `*_FROZEN.json`, aux empreintes Git blob vérifiées par `pilot.py`. Deux familles d'entraînement et trois familles de test séparées, cinq cas cachés par famille.

1. **A** : répondre directement aux trois nouveaux exercices, 660 tokens maximum par réponse.
2. **Pratique** : essayer deux exercices de départ, choisir automatiquement celui sur lequel le modèle échoue le plus, recevoir un feedback exécutable de développement, corriger sa solution. Une leçon candidate n'entre en mémoire de contexte que si la correction est sûre, réussit tous les tests de développement et fait mieux que l'essai initial.
3. **B** : répondre aux *mêmes* trois exercices avec cette seule leçon candidate, même nombre de générations et même plafond que A. Le supplément de contexte et le coût de formation sont enregistrés ; l'effet n'est **pas** causalement isolé.
4. **C** : entraînement paramétrique **non autorisé**. Le Hub #235 exige davantage d'exemples indépendants vérifiés, des familles variées et une nouvelle cohorte gelée. Le LoRA SFT01 reste intact.
5. **Score** : le programme séparé `score.py` lit pour la première fois `EVAL_SEALED_FROZEN.json`, et note les réponses déjà sauvegardées.

## Exécution

```sh
python -m unittest discover -s research/learning_hub/self_teach01 -p test_self_teach01.py -v
# Sur un serveur llama.cpp local contenant le modèle Qwen2.5-3B épinglé :
python research/learning_hub/self_teach01/pilot.py --server http://127.0.0.1:8080 --output /tmp/omega-self-teach-raw.json
python research/learning_hub/self_teach01/score.py --raw /tmp/omega-self-teach-raw.json --output /tmp/omega-self-teach-score.json
```

Workflow GitHub : `omega-self-teach01.yml`, un seul pilote CPU réel après ouverture de la PR et préflight hors ligne. 0 API payante, aucune clé, aucune écriture sur `main`. Les 15 cas cachés sont **consommés après la première notation** ; tout nouveau test de transfert réclame une nouvelle cohorte et son gel avant l'essai.

## Ce que ceci ne prouve pas

Un score vert du CI prouve la mise en œuvre, pas l'acquisition d'une compétence. Une leçon générée depuis un seul exercice n'est qu'une hypothèse pédagogique, même lorsque son programme passe les tests limités. B peut faire moins bien que A, ou ne disposer d'aucune leçon admissible. Un bénéfice sur trois exercices synthétiques n'établit ni une AGI, ni une compréhension mathématique, ni un transfert général. Aucun appel dans cette PR n'affirme avoir formé les poids d'Omega.

**Étape décisive suivante** : sur un corpus externe libre et vraiment indépendant, comparer A/B/C avec un coût total comparable, des tests de rétention, la vérification des corrections par oracles distincts et un entraînement LoRA autorisé seulement après franchissement des verrous. Les résultats négatifs demeurent archivés et `main` reste inchangée.
