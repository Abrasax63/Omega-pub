# Provenance — `npm pack` zsh relié à un artefact public

19 novembre 2026, 17 h 29 (Paris). **VÉRIFIÉ — gain externe partiel, blocage Windows nouveau.** Branche `work/omega-provenance-lab`, départ `7a38095338f07af879cfe470495a40085ad1a914`. Le cycle précédent consigné était mathématique (`437ed7f260a5c64ba3d9f8fa976a0038eecf2dad`), donc ce cycle est de provenance.

## Question et engagement préalable

Question réfutable : l'adaptateur peut-il relier une commande `npm pack` réellement exécutée dans un journal GitHub zsh au `.tgz` archivé, sans confondre une copie et sans lire les réserves avant `propose` ? Le [pré-enregistrement](FISHYJOES_NPM_PACK_PREREG_2026-11-19.md) a fixé avant lecture des journaux réservés : entraînement Ubuntu, réserves macOS et Windows, témoin `cp`, référence vide, comparateur fixe, zéro fausse confirmation, gain strict sur la référence et budget de trois journaux/trois ZIP.

Workflow inédit : [FishyJoes Node Runtime, run 44397873419](https://github.com/cricut/FishyJoes/actions/runs/44397873419), commit source `582c84dd228b633190bdcd04d99bd3fb3c2a8477`. La [définition épinglée](https://github.com/cricut/FishyJoes/blob/582c84dd228b633190bdcd04d99bd3fb3c2a8477/.github/workflows/node-runtime.yaml) exécute `set -euxo pipefail`, `npm pack`, puis `actions/upload-artifact@v7` sur `*.tgz`.

## Défaut reproduit et correction candidate

Sur l'extrait Ubuntu, l'adaptateur antérieur rendait `complete=false`, zéro écrivain, malgré la ligne zsh exécutée `npm pack` et la ligne `npm notice filename`. La correction candidate reconnaît uniquement une trace zsh `+...> npm pack` accompagnée d'un unique nom `.tgz` identique à la cible; doublons ou ambiguïtés restent fermés. Le comparateur fixe reconnaît la même opération comme `recalcul`. Deux tests ciblés couvrent succès et doublon contradictoire.

Le raccord hors ligne imposé a été vérifié (`Omega_raccord_horaire_PR81.zip` SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`; patch `b89e1a0422fe10dcadf8b4020f916569321e40e06815f8a686d7830ec104bbf3`). Dans la copie temporaire, `git apply --check` puis `git apply` ont réussi après matérialisation sur la base sans `provenance_offline.py`.

Ordre respecté :

1. `provenance_offline.py propose baseline.json training.json proposal.json` sur Ubuntu seulement;
2. lecture des deux journaux réservés et téléchargement des ZIP;
3. `provenance_offline.py check baseline.json reserved.json proposal.json`.

Le programme a choisi le préfixe `npm`; la règle candidate est `npm -> recalcul`. Empreintes : entraînement `071edd6860c0d2e7ea7dfa63017e722a3a7d83509b1670069c310f6067909044`, réserve `e1e58f1e67c5b5f7897ee766535eca875ed8088419063870af4068e1733f3a85`, proposition `50ec464ff1b488590d35dd10728da660d9b169f1213ed8dfb4115b09af999955`, verdict `991fb35588e25554856573d6b9450c2eb78a8b5dfe513d891290a764dff76892`, adaptateur candidat `e7c800983513285c7bb17028f58c87083793e04cf5387ab8c7b18d718dda5c19`.

## Pièces et résultats

Les trois archives GitHub portent un digest indépendant et contiennent exactement le `.tgz` annoncé : Ubuntu `05efa846...338569`, macOS `87c49bc...93298`, Windows `5ecfb78f...4ef14`. Les extraits et manifestes publiés ici ne contiennent aucun secret ni corrigé privé.

Sur les trois réserves (macOS `recalcul`, Windows `recalcul`, témoin local `copie`) :

- référence : 0 fausse confirmation, 0 correcte, 3 abstentions;
- candidat : 0 fausse confirmation, 1 correcte, 2 abstentions;
- règle fixe : 0 fausse confirmation, 2 correctes, 1 abstention;
- `recommend_for_review=true`.

Le gain externe est le cas macOS réservé : +1 confirmation correcte contre la référence, sans faux positif. Il ne dépasse pas la règle fixe. La réserve Windows révèle un format Bash `+ npm pack` terminé par CRLF que le candidat zsh refuse : information nouvelle et reproductible, pas une régression sur une confirmation antérieure. Le témoin `cp` reste abstention du candidat et confirmation correcte du comparateur fixe.

Tests : `python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q` — 68 tests réussis en 0,034 s. Aucun workflow déclenché, aucun appel payant, aucun jeu gelé modifié.

## Décision et prochain test

**Statut : IMPLÉMENTÉ, EXÉCUTÉ, VÉRIFIÉ.** La correction zsh est conservée car elle produit un gain réservé mesuré et tous les tests passent. Elle reste candidate, sans promotion canonique : couverture 1/2 des plateformes externes et performance inférieure au comparateur fixe.

Prochain test décisif : sur un nouveau run public distinct, pré-enregistrer puis tester une normalisation CRLF et la forme Bash `+ npm pack`, sans réutiliser les réserves de ce cycle; exiger un second gain externe et zéro faux positif sur une commande `npm publish` contradictoire.
