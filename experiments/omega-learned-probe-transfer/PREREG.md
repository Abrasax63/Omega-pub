# Transfert d'une méthode conçue après observation

Ce pilote reprend le modèle CPU de la PR #200. Les pilotes #141 et #150
fournissaient des exemples ou des sources sélectionnés à l'avance. Ici,
le modèle choisit une expérience, reçoit ses propres observations
et rédige ensuite la méthode qui sera éventuellement rappelée.

## Acquisition
1. Un premier appel choisit deux mots de longueur 2 à 5 sur les commandes
   A et B et prédit SAME ou DIFFERENT pour l'affichage final. L'appareil
   repart de zéro à chaque mot. Les règles internes lui sont cachées.
   Un mot valide est un essai. Deux essais maximum, sans nouvel appel en
   cas de sortie invalide. Une réussite de la phase source demande une
   différence observée à composition identique, quelle que soit la justesse
   de la prédiction initiale. Conserver la prédiction et son éventuelle réfutation.
2. Un deuxième appel reçoit la trace réelle et écrit une note courte
   avec méthode, limite et prochain essai en cas d'échec de la méthode.
   Figer la trace et la note avant toute présentation d'un cas de transfert.

## Transfert contre témoin
- Deux tâches inédites pour ce pilote, dans un cadre lexical distinct
  de la source et sur des systèmes finis fabriqués pour l'expérience.
  Un cas exige d'isoler l'effet de l'ordre. Dans l'autre, les deux
  explications sont invariantes par permutation et une variation de
  composition est nécessaire. Les règles candidates sont visibles et
  le modèle décide du probe. Fiches et oracles figés avant les six appels.
- Même modèle, prompt de tâche, trace source commune, température 0,
  graine 19 et plafond de 64 jetons générés par appel cible. Un appel
  par cas et par bras avec conversations indépendantes.
  Seul le bras MEMO reçoit la note effectivement écrite par le modèle.
  Le bras SANS_MEMO reçoit un emplacement neutre. Même plafond d'entrée,
  mesurer les jetons effectivement consommés sans postuler leur égalité.
  Alterner l'ordre des bras entre les deux tâches.
- Aucune exécution de texte produit. Le juge exact accepte seulement le
  choix d'un type d'expérience et deux mots. Il exige une composition
  égale sur le cas ordre, différente sur le cas limite, et des
  prédictions SAME/DIFFERENT opposées entre les deux règles candidates.
  L'oracle calcule et archive ces prédictions pour le probe réel.
- Critère primaire, sur ces deux fiches seulement : source réussie,
  note réelle non vide, MEMO 2/2 et MEMO strictement meilleur que
  SANS_MEMO. Préserver les résultats d'égalité, pertes et échecs du
  cas limite, ainsi que les erreurs d'infrastructure. Un faux transfert
  est un choix ORDRE sur le cas limite, indépendant du statut du run.
- Aucun ajustement des poids. Mesure d'une note réinjectée en contexte,
  sur une paire synthétique, sans validation externe ni portée générale.
  Archive de l'acquisition avant le transfert et des générations avant
  le score. Branche brouillon, aucun changement de main, aucune API payante.
