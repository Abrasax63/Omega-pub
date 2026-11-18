# Omega — Du texte cité à un contre-exemple Δ_h

Le [pilote](delta_bridge.py) reconnaît un ensemble explicite de formulations portant sur une seule propriété : « Δ_h est toujours vide » pour une dynamique totale déterministe sur au plus quatre états, selon que l'observation est injective ou arbitraire sur son image. L'horizon est limité à cinq pas. Les hypothèses, la conclusion, les citations et le blob source sont associés à un contrat. Chaque affirmation acceptée passe le contrôle de citations de reader_bridge12 avant le calcul. Une formulation non reconnue, un champ absent, une hypothèse contradictoire ou un contrat JSON divergent des citations provoque l'abstention. La commande rejette un fichier JSON illisible ou dont la racine n'est pas un objet.

Le vérificateur compare les chemins du graphe observé à de vraies trajectoires. Les observations sont énumérées à renommage près. En cas de réfutation, il renvoie T, π, les deux extrémités et un chemin observé que la dynamique ne réalise pas. Une confirmation porte exclusivement sur la borne et les hypothèses cherchées.

## Résultat

Protocole épinglé au commit `1d35772562a3f5b3663b91a79834ee64d6678a47`. Le véritable plafond implémenté est de 3 984 systèmes par énoncé, contre la borne supérieure de 4 139 annoncée dans le protocole. Code et contrôles épinglés au commit `f2aa396213bdf21e206e8d0fb8c762e0d1963a08`. Cohorte synthétique de 24 énoncés privés, SHA-256 `5658b1fa1932d101e480e0a1925d0ae10e30f694c67beacbab40b000cacdda56`.

| Mesure | Conclusion extraite, sans calcul | Avec le vérificateur |
| --- | ---: | ---: |
| Affirmations correctes sans calcul | 8 | 0 |
| Affirmations fausses laissées sans contestation | 8 | 0 |
| Confirmations bornées | 0 | 8 |
| Réfutations avec témoin validé indépendamment | 0 | 8 |
| Abstentions sur les énoncés ambigus | 8 | 8 |
| Systèmes effectivement examinés | 0 | 1 416 |
| Maximum effectivement examiné sur un énoncé | 0 | 288 |

Les huit tentatives distinctes de remplacer « arbitraire » par « injective » dans une proposition ont été rejetées avant tout calcul. **8/8 tests de calibration réussis**, dont 720 comparaisons pour 1 à 3 états et 1 à 5 pas avec une seconde implémentation qui énumère toutes les suites d'observations. Cette expérience utilise un proposant déterministe dans les deux bras, le même plafond et zéro inférence de modèle. Le bras sans calcul restitue la conclusion de la source ; il sert de contrôle pour isoler la valeur du vérificateur. L'expérience mesure la chaîne logicielle dans une grammaire bornée. La comparaison avec une réponse directe d'un vrai modèle reste à exécuter sur de nouveaux cas.

## Exemple public de calibration

Depuis la racine du dépôt :

```sh
pilot=research/omega-100/delta-pilot
cat > /tmp/omega-delta.md <<'SOURCE'
On considère au plus 3 états et une dynamique déterministe totale.
On fixe l’horizon à 2.
L’observation est arbitraire sur son image.
Alors Δ_h est toujours vide.
SOURCE
python "$pilot/delta_bridge.py" /tmp/omega-delta.md --emit-proposal > /tmp/omega-delta.json
python "$pilot/delta_bridge.py" /tmp/omega-delta.md --proposal /tmp/omega-delta.json
python -m unittest discover -s "$pilot" -v
```

Ce cas rend T=(0,0,1) et π=(0,1,0) sur les états 0, 1 et 2. Le graphe observé contient le chemin 0→0→1, tandis que T² envoie chacun des trois états sur l'état 0, dont l'observation vaut 0.

Le point d'entrée `--proposal` accepte un JSON externe au format qu'illustre `--emit-proposal`. Pour cette version, le contrat et ses citations doivent coïncider avec la lecture reconnue par la grammaire. Une mise à l'épreuve du proposant réel devra enregistrer aussi les échecs de schéma, les extractions correctes et les abstentions, avant de mesurer les verdicts du vérificateur.

## Essai apparié avec un modèle local

Le [protocole épinglé](https://github.com/Abrasax63/Omega-pub/commit/cd6b0780d793ba5eed1b28d57e0885743bfe3cc8) fixe la comparaison entre une décision directe et une proposition que le vérificateur examine. [paired_eval.py](paired_eval.py) utilise le même modèle local et le même plafond de 700 tokens de sortie, alterne l’ordre des bras et associe le résultat à l’empreinte du modèle. Le coût total est mesuré séparément : compteurs de tokens, durée déclarée par Ollama et nombre de systèmes évalués par Omega. Le rapport conserve les contre-exemples produits, les réponses incorrectes et les abstentions excessives ou justifiées. [API Ollama](https://docs.ollama.com/api/generate)

Cohorte synthétique réservée : 24 documents distincts des fichiers du premier pilote, huit par verdict de référence. Les confirmations comprennent quatre cas où l’observation est arbitraire et où la borne de deux états suffit. Les cas partagent la grammaire du pilote. Empreinte normalisée des sources : `ca2316d07dd1da9d9a848c5e82702b562dae45a0bade28efb0f74163a7fdabf5`. Empreinte normalisée du corrigé : `4ee955ddc441ceb033257741ca078bba552757e4dc35c3ee907640eccd0d5fad`. Les fichiers sources et corrigé restent hors du dépôt public.

Vérifications : 12 tests locaux passent et un essai de bout en bout traite 24 paires, soit 48 réponses simulées. L’essai de connexion réelle à Ollama a renvoyé `Connection refused`. Zéro génération réelle, aucun résultat comparatif sur un modèle.

Avec Ollama local et un modèle déjà installé, depuis la racine du dépôt :

```sh
pilot=research/omega-100/delta-pilot
python "$pilot/paired_eval.py" collect \
  --sources /chemin/sources.json --model "$OMEGA_OLLAMA_MODEL" --output /tmp/omega-replies.json
python "$pilot/paired_eval.py" score \
  --sources /chemin/sources.json --run /tmp/omega-replies.json \
  --gold /chemin/gold.json --output /tmp/omega-score.json
```

Définir `OMEGA_OLLAMA_MODEL` sur le nom exact du modèle installé. La génération ne reçoit pas le chemin du corrigé. Le calcul du score se fait après la collecte.

## Antériorité et réduction du problème Δ_h

Le protocole « modèle ouvert, réponse directe et calcul exact » avait déjà été proposé dans [#74](https://github.com/Abrasax63/Omega-pub/pull/74) et [#75](https://github.com/Abrasax63/Omega-pub/pull/75). [#174, run 44172032656](https://github.com/Abrasax63/Omega-pub/actions/runs/44172032656) a réellement exécuté Qwen sur six questions FOLIO : six réponses du moteur local, cinq JSON valides, aucune formalisation complète. [#178, run 44176803218](https://github.com/Abrasax63/Omega-pub/actions/runs/44176803218) a produit dix candidatures, dont huit avec citations littérales exactes et aucune formalisation structurelle complète. La couche d’inférence existante est donc à réutiliser pour tout transfert ultérieur. Le banc apparié ci-dessus reste une préparation sur Δ_h sans inférence réelle.

Le contrat actuel porte sur l’énoncé universel « Δ_h est vide pour toutes les dynamiques totales déterministes d’au plus N états », avec observation injective ou arbitraire et h ≥ 1. Dans ce périmètre, la décision exacte se réduit aux cas suivants :

- Si h = 1, Q et R₁ coïncident par définition.
- Si π est injective, chaque observation identifie son état. Chaque chemin observé se relève alors en trajectoire réelle.
- Si N ≤ 2, toute observation est injective ou constante. Dans le cas constant, le graphe observé est constitué d'une boucle, réalisée à tout horizon.
- Si N ≥ 3, h ≥ 2 et π est arbitraire, le même témoin T=(0,0,1), π=(0,1,0) suffit. Le graphe observé contient la boucle 0→0 et l’arête 0→1. Une succession de h−1 boucles suivies de cette arête atteint 1 en h pas observés. Or Tʰ envoie les trois états sur 0 dès h=2.

**Contrôle exécuté** : la règle concorde avec les 40 contrats admis par le pilote, 32 confirmations et 8 réfutations. Le vérificateur historique a examiné 5 944 systèmes au total. Pour chacune des huit réfutations, le témoin fixe a été validé par l’oracle indépendant. La règle donne ici la décision par trois conditions et, si nécessaire, un témoin constructif. Il s’agit d’une réduction du problème borné du pilote, sans revendication de nouveauté bibliographique. Le vérificateur courant conserve ses budgets et son comportement.

```sh
PYTHONPATH=research/omega-100/delta-pilot python - <<'PY'
from itertools import product
from delta_bridge import Contract, MAX_SYSTEMS, verify
from test_delta_bridge import valid_witness

checks = counterexamples = 0
for n, h, mode in product(range(1, 5), range(1, 6), ("injective", "arbitraire")):
    contract = Contract(n, h, mode)
    reference = verify(contract, MAX_SYSTEMS)
    refuted = mode == "arbitraire" and n >= 3 and h >= 2
    assert reference["status"] == ("REFUTED" if refuted else "CONFIRMED_WITHIN_BOUND")
    if refuted:
        assert valid_witness({"contract": vars(contract), "witness": {
            "T": [0, 0, 1], "pi": [0, 1, 0], "endpoints": [0, 1],
            "observed_path": [0] * h + [1],
        }})
        counterexamples += 1
    checks += reference["systems_checked"]
assert (checks, counterexamples) == (5944, 8)
PY
```
