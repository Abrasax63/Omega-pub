# Cycle de provenance — FishyJoes Bash/CRLF

## 1. Point de départ

- Horodatage : 2026-11-19 21:08–21:22 Europe/Paris.
- Branche : `work/omega-provenance-lab`.
- SHA initial : `b1f5725df2d74b1cdaeb5ca1a6a4e555b5bc6046`.
- Dernier cycle évité : adaptateur FishyJoes zsh/`npm pack` du run `44201520548`.
- Statut final : **VÉRIFIÉ** pour le raccord Bash/CRLF ; **INDÉTERMINÉ** quant à un gain de classification externe au-delà de la règle fixe.

## 2. Question falsifiable et critères figés

Question : une trace GitHub Windows Bash terminée par CRLF, contenant `+ npm pack`, peut-elle être structurée sans que `npm publish` soit pris pour le producteur de l'archive ?

Avant lecture de la réserve, le préenregistrement a fixé :

- entraînement : run `44201520548`, job Windows `134456542583` ;
- réserve distincte : run `44172435750`, jobs Windows `134354816411` et macOS `134354816556` ;
- témoin négatif : `npm publish <archive.tgz>` sans `npm pack` ;
- référence : extracteur au SHA initial ;
- comparateur fixe : `npm pack → recalcul`, sinon `indéterminé` ;
- succès : 2/2 archives réservées reconnues, 0 faux positif sur le témoin, ancien zsh préservé, tests verts ;
- budget : 1 job d'entraînement, 2 jobs réservés, métadonnées de 3 artefacts au plus, aucun appel payant.

Le fichier de préenregistrement est `provenance_trials/fishyjoes-bash-crlf-prereg-2026-11-19.md`.

## 3. Action réellement effectuée

1. Le raccord hors ligne fourni a été matérialisé et contrôlé :
   - ZIP SHA-256 : `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd` ;
   - patch SHA-256 : `b89e1a0422fe10dcadf8b4020f916569321e40e06815f8a686d7830ec104bbf3` ;
   - `git apply --check` puis application dans la copie temporaire.
2. L'extracteur de référence a reproduit le défaut : abstention sur le cas Windows Bash/CRLF, mais verdict `recalcul` sur le cas macOS zsh.
3. Le candidat reconnaît exactement `+ npm pack`, neutralise le CR final et ferme la fenêtre `pack` dès `npm publish`. Une seconde notice de nom émise pendant la publication ne double donc plus la preuve du paquet.
4. `provenance_offline.py propose` a été exécuté avant toute lecture réservée. Le programme a choisi le préfixe `["npm"]`.
5. Après seulement, `provenance_offline.py check` a lu trois cas réservés : Windows, macOS et le témoin `publish`.
6. Les métadonnées GitHub attestent séparément les artefacts réservés :
   - Windows `14369755073`, digest `62382e960b4d8897ccd33670acbc8ef11e479d9c9aea24df5811c5ed2ae953f3` ;
   - macOS `14367878617`, digest `56370d176ddd685e09fb2b2210e025d8bdea98c6035ed585130a31a6aff1d790`.
   Le run réservé pointe le commit `ebb8bb701cc6614e2d0f4b5060470ef2a3cb9c95`.

## 4. Preuves et empreintes

- Entraînement : `10870bc0d1082ba9df0f6ecc7be431ae35eaf0460e6e22fa91bfd1686a6f8c3a`.
- Manifeste d'entraînement : `94514b0d8374c4dc9a3f5222717b8815b983fdc466fe83ebf070446bbf45589c`.
- Proposition : `c0ea55ef5ee726c4b8f317df5978e2a805d0957da056719184fbea869efe6bca`.
- Réserves :
  - Windows : `ba331c7554636291fb8d23d6a66f405fa9afc0e02d9eed6ddd06be8bb24f4642` ;
  - macOS : `d3f2ab6a98ad1357a00827899a5205490dca3474ea747b94507f3946ad55a653` ;
  - témoin publication : `4c267384327c6c00a5f05955b867a2ed3a223680ee672a96330372b0ad2dc273`.
- Manifeste réservé : `e4ec70966a95168626d4bd00cb625cd736ee3a5d6c2c3563d608bb49cdc1cb05`.
- Résultat : `e906ffe62ad1e14570b3f404bed87bb6ca54cd00dd7cf79000a94f1d4f436e19`.
- Extracteur candidat : `964c5407ecaa9fd5af95639407c030236ecb696c9597c18149ae6a91138c1335`.
- Tests du raccord : `c2d0701aa3a6a8747d9d35ae883c83e24288697e835c5275ab2309656df0b773`.

Sources vérifiables :

- entraînement : https://github.com/cricut/FishyJoes/actions/runs/44201520548/job/134456542583
- réserve Windows : https://github.com/cricut/FishyJoes/actions/runs/44172435750/job/134354816411
- réserve macOS : https://github.com/cricut/FishyJoes/actions/runs/44172435750/job/134354816556

## 5. Comparaison et métriques

| Mesure | Référence d'extraction | Candidat | Règle fixe |
| --- | ---: | ---: | ---: |
| Archives réservées structurées | 1/2 | 2/2 | n/a |
| Confirmations correctes sur 3 cas | 1 | 2 | 2 |
| Faux positifs | 0 | 0 | 0 |
| Abstentions | 2 | 1 | 1 |
| Témoin `npm publish` | abstention | abstention | abstention |

Gain mesuré du **raccord brut → structuré** : +1 archive réservée, soit couverture 50 % → 100 % sur les deux systèmes du run réservé. Les 72 tests existants et ajoutés passent.

Il n'y a toutefois **pas de gain externe du vérificateur par rapport à la règle fixe** : candidat et règle fixe font 2 confirmations correctes, 0 faux positif et 1 abstention. La référence déclarative du vérificateur reste donc inchangée. Seul l'adaptateur de trace est conservé, car son gain d'extraction est mesuré et sans régression observée.

Coût : zéro appel payant ; trois lectures de jobs (une d'entraînement, deux réservées), deux lectures de métadonnées d'artefacts, 72 tests locaux. Les archives ont été demandées, mais leur contenu binaire n'a pas été rendu inspectable localement par l'interface ; je ne prétends donc pas avoir recalculé leurs digests. Les digests consignés sont ceux rapportés par l'API GitHub.

## 6. Commandes reproductibles

```sh
git apply --check omega-provenance-offline.patch
git apply omega-provenance-offline.patch
python3 provenance_offline.py propose \
  provenance_trials/fishyjoes-bash-crlf-baseline.json \
  provenance_trials/fishyjoes-bash-crlf-training.json \
  provenance_trials/fishyjoes-bash-crlf-proposal.json
python3 provenance_offline.py check \
  provenance_trials/fishyjoes-bash-crlf-baseline.json \
  provenance_trials/fishyjoes-bash-crlf-reserved.json \
  provenance_trials/fishyjoes-bash-crlf-proposal.json
python3 -m unittest discover -v
```

## 7. Décision et prochain test décisif

- Adaptateur Bash/CRLF : **conservé**, gain mesuré et tests verts.
- Règle proposée `npm → recalcul` : **non promue** ; parité avec la règle fixe.
- Jeux gelés : inchangés.
- Prochain test : sélectionner un workflow externe qui n'est pas FishyJoes, préenregistrer une archive et son digest, puis appliquer le raccord au journal complet non découpé. Ce test doit comporter une commande `npm publish` ou une seconde notice contradictoire pour éprouver la segmentation, et une vérité terrain d'artefact séparée.

