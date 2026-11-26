# Préenregistrement — FishyJoes Windows Bash/CRLF

- Horodatage : 2026-11-19 21:08 Europe/Paris.
- Branche : `work/omega-provenance-lab`, SHA initial `b1f5725df2d74b1cdaeb5ca1a6a4e555b5bc6046`.
- Question : une trace GitHub Windows Bash terminée par CRLF, contenant `+ npm pack` et le nom de l'archive, peut-elle devenir une trace structurée sans assimiler `npm publish` à un producteur ?
- Entraînement : run FishyJoes `44201520548`, job Windows `134456542583`.
- Réserve, non lue avant la proposition : run distinct `44172435750`, jobs Windows `134354816411` et macOS `134354816556`.
- Référence : extracteur du SHA initial ; comparateur fixe : `npm pack → recalcul`, sinon abstention.
- Témoin négatif : extrait `npm publish <archive.tgz>` sans commande `npm pack`.
- Succès : deux confirmations exactes sur les jobs réservés, abstention sur le témoin négatif, ancien cas zsh inchangé et tous les tests verts.
- Échec : faux positif sur `npm publish`, conflit accepté, régression zsh ou test rouge.
- Budget : un job d'entraînement, deux jobs réservés, trois archives GitHub au maximum ; aucun appel payant.

