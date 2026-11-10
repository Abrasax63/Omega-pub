# Télémétrie P5 — schéma de collecte

**Version :** 0.1.0  
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
