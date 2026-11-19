# Test de liaison entre hypothèse et conclusion

Ce pilote est empilé sur le correctif Reader12 de la PR #179 au commit
`def8bac9fdafd81422d40c4c45ac3652a6d47e35`. Il teste un exemple synthétique
minimal, décliné en deux fiches. Le statut ou le nom de la source ne révèle
aucun verdict. Les deux fiches présentent les mêmes deux lois candidates
et la même propriété d'injectivité. Une seule ligne change, celle qui
désigne le régime auquel la conclusion candidate doit être rattachée.

## Protocole avant toute inférence

- Figer les deux Markdown et la référence des citations lors du commit
  d'implémentation, après ce protocole et avant l'exécution. La référence est
  établie directement à partir du texte et vérifiée par un argument
  mathématique séparé. L'annotation précède et ignore les réponses du
  modèle. Les fiches et l'annotation sont créées pour ce pilote par le même
  auteur et ne constituent pas une validation humaine externe.
- Fournir au modèle et au témoin la même liste de lignes numérotées reconstruite
  à partir des paquets de Reader12, avec les deux formules, la phrase de
  sélection, le domaine et la conclusion visibles. Maximum dix paquets par
  fiche. Le JSON de référence, les chemins et le SHA des fiches n'entrent pas
  dans le prompt. On demande trois numéros de ligne dans l'ordre domaine,
  loi applicable, conclusion, ou NONE. Le témoin choisit le premier domaine
  reconnu, la première ligne de loi et la dernière ligne de formule
  comme conclusion, en ignorant le nom du régime applicable. Il est figé avant
  l'inférence et mesure un choix par position.
- Utiliser Qwen2.5-Coder-3B-Instruct Q4_K_M, avec les empreintes et le moteur
  épinglés de la PR #184. Une génération CPU par fiche, température 0,
  graine 19 et maximum 64 nouveaux jetons par génération. Aucun outil
  ni accès réseau pour le modèle. Les réponses erronées et les erreurs
  d'infrastructure sont conservées. Une sortie invalide ne déclenche aucune
  nouvelle génération.
- Archiver les sorties brutes, les prompts et l'usage avant la notation.
  Vérifier l'exactitude des citations avec le gate de la PR #179, puis les
  trois rôles et les lignes choisies avec la référence. Utiliser les
  fragments issus de la source pour construire un contrat fermé et énumérer
  toutes les applications sur des ensembles de 1 à 3 éléments. Évaluer
  la vérité sous la loi réellement choisie, avec le premier contre-exemple
  éventuel et les effectifs testés. L'oracle ne reçoit aucun nom de fiche,
  aucune annotation et aucun verdict souhaité. Une loi incorrecte reste un
  échec d'extraction même si l'oracle donne une réponse déterminée.
- Réussite de ce pilote si les deux extractions du modèle sont fidèles et
  si le verdict sous la loi citée est vrai sur le domaine borné dans une
  fiche et réfuté dans l'autre. Le témoin est noté avec le même protocole.
  Deux fiches constituent un test du raccord sur une paire contrôlée.
  Elles ne mesurent pas la fidélité sur des documents libres.
- L'expérience s'exécute sur une branche dédiée et un runner GitHub hébergé,
  avec un modèle CPU sans API payante. Les propositions restent en
  quarantaine. Aucune publication de règle Horn ni certification.
