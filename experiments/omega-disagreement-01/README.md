# OMEGA-DISAGREE-01

Sélecteur expérimental de mots d'équivalence (EQ) **par désaccord de variantes locales compatibles avec les observations payées**. Il ne modifie pas le moteur L* des quatre références.

- **Préenregistrement antérieur au code** : commit [0019fbb](https://github.com/Abrasax63/Omega-pub/commit/0019fbb181032944491bcc56a240159da43bb95c) ; [contrat](PREREG_2026-11-17.md).
- **Motivation auditée, non utilisée pour ajuster après coup** : [analyse #140](../../research/audits/OMEGA-DISAGREE-01-DIAGNOSIS.md).
- **Code** : disagreement_lab.py. Le sélecteur lit seulement la proposition L* courante et les réponses MQ/EQ terminées du compteur. Aucun accès à la table cachée, au rapport réservé ni à la certification BFS. Mutations de sortie ou de destination d'une arête, filtrage strict par traces, choix d'un mot de longueur 10 maximisant la diversité des prédictions. Repli explicite sur COVER quand aucune alternative ne survit.
- **Contrôles** : test_disagreement.py. Vraie évaluation indépendante seulement après apprentissage.
- **Dépenses** : plafond de 300 ou 500 symboles MQ+EQ, test par mot EQ exactement 10 symboles, 32 essais maximum par hypothèse.

Installation gratuite (Python 3.11) :

~~~sh
python -m pip install aalpy==1.6.2
python -m unittest discover -s experiments/omega-disagreement-01 -p test_disagreement.py -v
python experiments/omega-disagreement-01/disagreement_lab.py --output evidence/report.json
~~~

Le pilote complet utilise 48 nouvelles machines et cinq bras (480 apprentissages). Les anciens résultats restent intacts. Les tests verts n'impliquent **aucun gain scientifique** ; consulter les artefacts du run et le critère gelé. Garder la PR en **DRAFT**, pas de fusion, pas d'API payante.
