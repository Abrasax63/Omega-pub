# P5 — premier pilote réel sans API payante ni calcul sur smartphone

**2026-11-12 — branche de travail expérimentale, à ne pas confondre avec le holdout P5 v0.5.**

## Ressources et coût

- Calcul exécuté **à distance dans GitHub Actions**, sur `ubuntu-latest` **standard** du dépôt **public** Omega-pub. Aucune puissance locale/Android n'est utilisée.
- GitHub annonce la gratuité de l'exécution sur les runners standard des dépôts publics : https://docs.github.com/en/billing/concepts/product-billing/github-actions (des limites, indisponibilités de ressources ou règles anti-abus peuvent s'appliquer). **Aucun runner large/payant**, aucun service API génération payant.
- Modèle public téléchargeable : [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) sous Apache 2.0, chargé sur CPU par Transformers.
- **Aucune clé OpenAI**, ni clé Hugging Face, ni secret GitHub utilisés. L'exécution peut échouer si l'infrastructure GitHub ou le téléchargement Hugging Face ne sont pas disponibles : ne jamais interpréter cet échec comme un résultat du benchmark.

## Protocole

- **6 exercices publics, connus de l'auteur**, répartis en 2 propositions mathématiques, 2 congruences et 2 taux globaux ; **3 stratégies A/B/C**, donc **18 générations réelles sur CPU** si le workflow réussit.
- A : réponse directe ; B : perspectives fixes ; C : perspectives choisies par le vrai `planner.plan_mission`. Même contexte, même modèle, même plafond de 80 tokens nouveaux, séquencement mélangé, pas de mémoire entre les appels.
- Le modèle ne voit pas la réponse attendue. La correction mécanique est très stricte : seule la dernière ligne `Réponse finale : CODE` est acceptée. Une réponse correcte mais non formatée peut être notée comme non conforme. Archiver la sortie originale pour audit humain.
- Les requêtes, réponses et notes **sont publiques**. Les fichiers privés `/Omega-Private/P5V05-Candidate-2026-11-11`, leurs corrigés, les 96 requêtes de P5 v0.5, et les clés API **ne sont ni lus ni copiés**.
- Il n'y a qu'une répétition, 6 cas construits par l'auteur et aucun évaluateur aveugle. Le modèle de 0,5 milliard de paramètres n'est pas GPT-6. **Cela teste le fonctionnement et donne une première observation exploratoire**, pas une preuve indépendante du gain général d'Omega.
- Exécution contrôlée par `.github/workflows/omega-p5-free-cpu-pilot.yml` ; vérification des 18 sorties et artifact JSON public conservé 3 jours. Les contrôles statiques précèdent l'installation du modèle et toute inférence.

## Interprétation scientifique

Rapporter séparément : réussite technique du workflow (oui/non), sorties réellement générées, précision avec le parseur strict, coût API OpenAI = 0 (aucun appel), coût GitHub **selon les règles de l'hébergement public** et ressources non garanties. Comparer A, B, C sans extrapoler au holdout privé.

Le test est distinct de P5 v0.5 et n'entraîne **aucune mutation de `main`**.
