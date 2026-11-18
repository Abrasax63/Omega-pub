# Omega — Du texte cité à un contre-exemple Δ_h

Le [pilote](delta_bridge.py) reconnaît un ensemble explicite de formulations portant sur une seule propriété : « Δ_h est toujours vide » pour une dynamique totale déterministe sur au plus quatre états, selon que l'observation est injective ou arbitraire sur son image. L'horizon est limité à cinq pas. Les hypothèses, la conclusion, les citations et le blob source sont associés à un contrat. Chaque affirmation acceptée passe le contrôle de citations de reader_bridge12 avant le calcul. Une formulation non reconnue, un champ absent, une hypothèse contradictoire ou un JSON non conforme provoque l'abstention.

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
