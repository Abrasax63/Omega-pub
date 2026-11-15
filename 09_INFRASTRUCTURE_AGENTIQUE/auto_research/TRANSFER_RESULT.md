# OMEGA-TRANSFER-01 — verdict empirique, 15 novembre 2026

**Statut : EXÉCUTÉ / RÉSULTAT NÉGATIF.** Il ne constitue pas une réfutation de toute intelligence auto-améliorative, seulement de la supériorité mesurée de ce candidat précis sur ce protocole.

- Protocole fixé **avant** le banc de mesure : [TRANSFER_PREREG.md](TRANSFER_PREREG.md), commit `5517108fd65620525c7e7d038860b4fa25ccbd7d`.
- Programme Qwen2.5-Coder-3B figé : [frozen_qwen3b_candidate.py](frozen_qwen3b_candidate.py), SHA-256 `121e09058b41984199ac870b6250882ffa4eddb5a4344b1fb1cd0d674296de5a`, originellement produit au [run 43693684837](https://github.com/Abrasax63/Omega-pub/actions/runs/43693684837).
- Premier test : [GitHub Actions 43728381972, SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43728381972), commit `5aeda7e996b80fa932cc18871227a9508df53353`. Les **54 tests unitaires ont réussi** et l'expérience a été exécutée dans Docker sans réseau, avec source en lecture seule.
- [Artefact JSON inspectable du run](https://github.com/Abrasax63/Omega-pub/actions/runs/43728381972/artifacts/14167730429), avec 64 cas mesurés et 16 cas h=0 de contrôle, sept mesures CPU par méthode et par cas, et les verdicts comparant les deux algorithmes classiques.

## Résultats

- Exactitude du candidat : **80/80 cas Q^h corrects** ; aucune divergence de `Delta_h` sur les cas de projection.
- Référence primaire : **la plus rapide, pour chaque cas, de deux exponentiations binaires classiques** (`square-scan` et `square-lowbit`). Cela est un **comparateur classique favorable**, mais sa sélection par minimum est volontairement conservatrice et n'établit pas une vitesse atteignable par un seul algorithme universel sans oracle.
- Moyenne géométrique du rapport vitesse (meilleure référence / Qwen) : **0,080298**, soit environ **12,45× plus de temps CPU** pour le code Qwen dans les conditions de ce test (inverse de 0,080298).
- Médianes des rapports par famille : bipartite 0,10228 ; complète 0,08491 ; cycle 0,06016 ; dense 0,09427 ; vide 0,03410 ; fonctionnelle 0,06228 ; projection 0,12430 ; clairsemée 0,09922. **0/8 familles positives**.
- Test de signe unilatéral selon le protocole : **p = 1,0** pour une supériorité du candidat. Ce chiffre n'est pas une analyse confirmatoire de puissance statistique.
- Les deux évaluations via le `gate.py` inchangé de la PR #83 rendent `REJECTED`.
- Verdict préenregistré : **NO_DEMONSTRATED_ADVANTAGE**. Aucun dépassement des méthodes classiques n'a été montré ; la supériorité n'est pas certifiée.

## Contrôles de fidélité

L'artefact contient :
- le SHA de la source Qwen et le SHA des entrées ;
- le SHA du manifeste évalué ;
- le commit exact du code exécuté ;
- l'empreinte de l'image Python Docker `python@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b` ;
- les résultats par cas et les médianes par bras, sans sélectionner de run favorable.

Cette cohorte est **nouvelle mais synthétique et publiquement générée**, pas un corpus externe confié à un évaluateur indépendant. Le CPU d'un runner partagé fluctue et la sélection du meilleur classique par cas est un oracle de référence volontairement strict. Ces limites sont incompatibles avec une conclusion universelle sur les capacités du modèle.

## Conséquence pour Omega

La chaîne **proposer → exécuter → vérifier → rejeter** fonctionne sur un modèle réel et un problème mathématique. Le résultat interdit néanmoins de présenter ce programme comme une découverte ou comme un progrès d'intelligence.

Pour la prochaine itération, garder le candidat rejeté et le protocole immuables, préparer **de nouvelles familles externes** et demander au modèle de proposer des optimisations du noyau d'exponentiation binaire plutôt que de recréer la multiplication itérative. Les prochaines propositions doivent être fixées avant d'ouvrir leurs propres tests réservés ; ne pas réutiliser `OMEGA-TRANSFER-01` pour décider de leur acceptation.

**Pas de fusion automatique, pas de promotion CORE, pas de modification de `main`.**
