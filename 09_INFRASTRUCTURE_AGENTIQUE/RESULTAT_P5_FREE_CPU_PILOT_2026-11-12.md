# P5 — résultat observé du premier pilote CPU distant, 12 novembre 2026

**Technique : TERMINÉ / 18 VRAIES INFÉRENCES / 0 APPEL API OPENAI / 0 CALCUL SUR LE SMARTPHONE.**

Sources : [GitHub Actions run 43180757608](https://github.com/Abrasax63/Omega-pub/actions/runs/43180757608) (**SUCCESS**) et [archive JSON brute des 18 réponses](https://github.com/Abrasax63/Omega-pub/actions/runs/43180757608/artifacts/13926222307).

- Exécution GitHub Actions sur un runner Ubuntu **standard**, dans le dépôt public. GitHub indique que ces runners restent gratuits pour les dépôts publics ; pas de runner élargi. Aucune variable OPENAI_API_KEY consultée, aucun service de génération API utilisé.
- Modèle réel : `Qwen/Qwen2.5-0.5B-Instruct`, révision rapportée par le fournisseur `7ae557604adf67be50417f59c2c2f167def9a775`, `transformers==4.51.3`, `torch==2.6.0`.
- 6 questions **publiques de calibration** × 3 stratégies A/B/C × 1 génération = **18 sorties réelles**. Pas le corpus privé P5 v0.5 ; aucun corrigé privé, aucune clé API, aucun système multiagent externe ; le véritable planificateur Omega n'a servi qu'à composer la perspective C.
- 80 tokens de sortie maximum par bras et par question. Inférence greedy et sessions sans historique partagé.

## Données mesurées par l'exécuteur

| Approche | Générations | Tokens entrée | Tokens sortie | Durée cumulée génération | Corrections au parseur strict |
|---|---:|---:|---:|---:|---:|
| A (directe) | 6 | 1 382 | 318 | 35,483 s | 0/6 |
| B (cinq perspectives fixes) | 6 | 2 198 | 294 | 36,130 s | 0/6 |
| C (perspectives adaptées) | 6 | 1 720 | 259 | 30,885 s | 0/6 |

**Attention : le dernier indicateur est un score mêlant exactitude ET conformité de format, pas l'exactitude sémantique.** Le parseur n'acceptait que la *dernière ligne exacte* `Réponse finale : [CODE]`. Dans les sorties brutes, plusieurs réponses formulent une conclusion intelligible ailleurs dans le texte, malgré l'échec de ce parseur. Ce **défaut d'instrumentation est constaté après exécution** et doit être traité sans post-sélection opportuniste.

Une vérification manuelle non aveugle montre, par exemple, que :
- `MATH-01` : les trois stratégies affirment à tort que toute extension est injective ; un contre-exemple est f(3)=1 ;
- `MATH-02` : les réponses B et C commencent par `OUI`, cohérent avec la permutation f(0)=1, f(1)=0, mais le parseur refuse les sorties non conformes ; la sortie A comporte un raisonnement contradictoire ;
- `DATA-02` : la sortie A contient « La réponse finale est "A". », cohérente avec le calcul 9/20 > 2/20, mais est refusée par le parseur ;
- `CRT-01` et `CRT-02` : plusieurs réponses se limitent à OUI ou A au lieu de produire les entiers demandés.

Ces constats sont **exploratoires et posthoc**, sans correction indépendante. Ne pas les transformer en amélioration d'Omega.

## Verdict et prochaine expérience

- **Débloqué :** des réponses de modèles sont désormais réellement exécutables à distance et gratuitement sans API OpenAI, avec journaux reproductibles et résultats accessibles depuis un smartphone.
- **Non établi :** aucun avantage mesuré crédible de C sur A ou B ; six cas faciles, un modèle 0,5 B, un seul passage, score strict inadapté, pas de correcteur indépendant.
- **Prochaine étape scientifique :** figer avant nouvelle exécution une évaluation tolérante aux variantes de format mais exigeante sur la cohérence sémantique, et un nouveau corpus public distinct ; ne pas réévaluer l'ancien échantillon comme un holdout. Puis reproduire avec davantage de cas et au moins un deuxième modèle libre si ressources disponibles.
- La branche de travail, la PR #47, `main` et le corpus P5 v0.5 privé ne sont pas modifiés par cette note.

**Aucune dépense API payante OpenAI ; les coûts réels éventuels d'autres produits ne sont pas mesurés ici.**
