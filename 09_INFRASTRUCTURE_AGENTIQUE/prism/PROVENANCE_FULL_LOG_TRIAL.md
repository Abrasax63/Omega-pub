# Essai sur journaux complets — 14 novembre 2026

Référence `1af9bd96c2c0c903db1c08825b2a2eaf32caef81`. Deux nouveaux jobs K3s de la même famille que les essais précédents, obtenus en lecture autorisée, [PR 14997](https://github.com/k3s-io/k3s/actions/runs/43561665973/job/132346516375) et [PR 14996](https://github.com/k3s-io/k3s/actions/runs/43553016671/job/132319505796). Les [scripts épinglés au premier](https://github.com/k3s-io/k3s/blob/692a0c7c97026538f1848cc4c6490c06689bfe62/scripts/package-cli#L74) et au [second checkout](https://github.com/k3s-io/k3s/blob/246abdbf6a01234749117fb49413d09394fc591a/scripts/package-cli#L74) prescrivent une copie locale. Le chemin de sortie a été repéré dans le journal pour formuler la question. Les méthodes reçoivent le journal complet, avec un budget d'une lecture chacune.

Candidat temporaire : appliquer BuildKit si un marqueur horodaté de commande BuildKit cp -av existe, Bash sinon. Fixe : appliquer BuildKit seul. Les deux confirment les copies sur les journaux d'origine, où Bash seul s'abstient. Si on retire le retour verbeux vers le chemin demandé, les trois s'abstiennent. Les contrôles dérivés sont des mutations et non des jobs distincts. Le test mesure un verdict de copie locale, sans vérification indépendante des octets. Parité au fixe, candidat non intégré, 24 tests locaux réussis. Aucun apprentissage sur traces annotées pendant ce cycle.

Lignes de résultat dans l'ordre job, Bash, candidat, fixe, SHA-256 du texte UTF-8 :

```text
0 indéterminé copie copie 3a5e6e5b35cb2f33813226d9bf2f065088f697138e8789eb46e2ebddb7fa1e8e
0 indéterminé indéterminé indéterminé c6faecd7f1d6652a39115190598d1e2881d4276d401e0e826eda1463e5ff70c1
1 indéterminé copie copie 3da0b415dd4d994c9ab9627075f3d295e5be3aef60aa57a197657e557781340d
1 indéterminé indéterminé indéterminé fce041e5aa481ee6f00511691f2f0f04b56cfe6a6b7d136f4beaf9ebdc2f85ae
```
