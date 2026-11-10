# Télémétrie P5 — schéma de collecte

**Version :** 0.2.0  
**Statut :** schéma et validateur disponibles ; aucune collecte A/B/C lancée.

## Objet

Le module `prism/telemetry.py` valide un enregistrement par appel fournisseur ou outil. Il sépare les mesures observées des mesures indisponibles et conserve la provenance de l'usage tokens et du coût.

Un enregistrement décrit notamment :
- l'expérience, le cas, le bras A/B/C et l'identifiant d'appel ;
- fournisseur, modèle, version éventuelle et identifiant de requête fournisseur ;
- horodatage avec fuseau, durée, statut et nombre d'appels outil ;
- tokens d'entrée, de sortie et d'entrée mis en cache ;
- source des tokens : réponse fournisseur, export fournisseur ou indisponible ;
- coût USD et source : fournisseur, export, calcul à partir d'une grille tarifaire ou indisponible ;
- CPU, mémoire maximale et octets lus/écrits, lorsque l'environnement les mesure ;
- statut de validation du résultat, distinct de toute affirmation de vérité.

## Règles de mesure

1. Les tokens ne sont qualifiés de rapportés par le fournisseur que si la donnée provient de sa réponse ou d'un export identifiable.
2. Les coûts calculés depuis une grille tarifaire doivent être étiquetés `computed_from_rate_card`, jamais confondus avec un coût directement rapporté.
3. Une mesure absente reste `null`. Le résumé renvoie un total `null` dès qu'une ligne du groupe manque cette mesure ; il fournit aussi le nombre de lignes manquantes. L'absence n'est jamais transformée en zéro.
4. Les métriques système sont facultatives et dépendent du harnais d'exécution. Le module ne les mesure pas lui-même.
5. Les enregistrements sont par appel ; le harnais doit éviter de compter deux fois les mêmes usages ou d'additionner un total de session avec les sous-appels qui le composent.
6. `result_validation_status` indique uniquement un état externe : `not_assessed`, `validated`, `rejected` ou `indeterminate`. Le validateur de télémétrie ne vérifie pas ce statut et ne certifie aucune vérité scientifique.

## API et tests

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism/` :

```python
from telemetry import validate_call_record, summarize_calls

validate_call_record(record)
report = summarize_calls(records)
```

```bash
python -m unittest -v
```

Les tests utilisent uniquement des enregistrements synthétiques. Ils ne contactent aucun fournisseur, ne génèrent aucune réponse A/B/C et n'accèdent pas au holdout P5.

## Limites actuelles

- Aucun adaptateur fournisseur ne collecte encore automatiquement les champs d'usage.
- Aucun collecteur CPU/RAM/I/O n'est branché.
- Le calcul de coût par grille tarifaire n'est pas implémenté.
- Aucune métrique n'a été collectée sur des missions réelles.
- Aucun gain d'efficience n'est démontré par ce schéma seul.


## Adaptateur OpenAI Responses API (premier connecteur)

`prism/openai_responses_adapter.py` transforme une réponse Responses API déjà obtenue
(en mapping ou objet SDK exposant `model_dump()`) en enregistrement du schéma commun.
Il lit les compteurs `input_tokens`, `output_tokens` et
`input_tokens_details.cached_tokens`, conserve l'identifiant de réponse et le modèle,
et marque la source comme `provider_response` uniquement si les deux compteurs principaux
sont présents. Un usage absent reste `null`. Un usage partiel ou invalide est rejeté.

La fonction `measure_call(call)` mesure le temps mural d'une fonction fournie par
l'appelant et renvoie la réponse, l'heure UTC de début et la durée. Elle ne contacte
aucun fournisseur. Le coût reste indisponible (`null`) tant qu'une source de coût
explicite n'est pas fournie.

Les tests de l'adaptateur utilisent des réponses synthétiques. Ils ne prouvent pas
encore la compatibilité avec une version précise du SDK en production ni une collecte
sur une requête réelle. Aucun secret, appel réseau ou holdout n'est utilisé.

## Consolidation du journal par appel

L'identité d'un appel est `(experiment_id, call_id)`. Pour un pilote, le
harnais fournit aussi `case_id`, `arm`, `repetition`, `operation_id` et
`attempt`. Une reprise garde l'opération et incrémente la tentative. Les
anciens enregistrements restent lisibles et une répétition non renseignée
reste inconnue dans le résumé par exécution.

Le contexte accepte le modèle demandé et la version vérifiée, le commit,
les empreintes des prompts et de la configuration, ainsi que l'empreinte
d'une décision de routage. Conserver les décisions et motifs exacts dans le
registre d'exécution privé. L'empreinte sert à relier les deux traces. Le
modèle retourné et les tokens viennent de la réponse fournisseur. La durée
vient de l'horloge monotone du harnais. Un coût calculé référence un barème
versionné. Les identifiants de requête et de réponse sont distincts.

`summarize_calls(records, by_execution=True)` regroupe par campagne, bras,
cas et répétition. La somme des durées d'appel peut différer du temps mural
de l'exécution. Une mesure manquante rend le total correspondant inconnu.
Un appel entier absent requiert un contrôle du manifeste de lancement.
Le harnais reste chargé de journaliser les exceptions de transport, les
timeouts et les reprises SDK, et de capturer les outils au point d'appel.
