# Pilote bibliothèque V19

Point d'entrée facultatif pour un cycle local, depuis la racine d'un clone complet d'Omega-pub.

```sh
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/v19_library/run.py --output /tmp/omega-v19-cycle.json
```

Utiliser un nouveau chemin par exécution. Les commits des PR #2, #5 et #18 doivent être présents dans le clone. Si une source manque, le pilote échoue avant d'émettre un verdict. L'inventaire de la PR #5 référence l'index et la fiche reconstituée de la PR #2. Le manifeste fixe explicitement les liens vers l'audit et le test de la PR #18. Le journal produit contient les chemins, commits et SHA-256. Les sources privées citées dans la fiche sont des références historiques.

## Exécution du pilote

Le fichier [result.json](result.json) conserve la sortie du script d'origine et le résultat de la projection par un second calcul. Les deux parcours partagent l'énumération des cycles. Le second reconstruit les contraintes et utilise l'union-find à parité sur **toutes** les composantes. Les 325 468 comparaisons global/local concordent dans le domaine testé. Le journal contient aussi un écart de sémantique du script historique.

Pour T = (0,0,3,4,2), B = (2,3,4), paire (0,1) et L = 2, la fusion impose c(0) ≠ c(1) et l'événement impose c(0) = c(1). L'ombre est donc vide. Le script historique renvoie les huit colorations de B car sa propagation démarre uniquement sur B. Cette contradiction est présente dans les deux graphes comparés. Elle ne fournit aucun contre-exemple à leur égalité.

## Raccord mathématique à relire

Pour comparer l'ombre globale au sous-graphe induit par les états visibles, il suffit que chaque chemin forcé entre deux ancrages (états du cycle et états touchés par les égalités de l'événement) soit visible. Les portions restantes des composantes forcées peuvent être coloriées indépendamment ou prolongées depuis leur seul point de contact. D'après la classification P1–P4 dans l'audit, les seuls sommets intérieurs d'un tel chemin appartiennent au noyau invariant. Dans le cas d'un 2-cycle tous deux sont vus au plus deux pas après une feuille ancrée, ou un pas après un sommet du noyau déjà ancré. Dans le cas de deux points fixes, chaque sommet intérieur est soit lui-même un ancrage, soit l'image d'une extrémité transitoire ancrée. Les ancrages de B ne peuvent appartenir à un noyau invariant.

Ce raisonnement vise l'égalité avec le **graphe induit construit en disposant de T**. Une suffisance à partir des seules données du préfixe demande en plus de déterminer les parités pertinentes à partir des images effectivement observées. En particulier, vérifier le noyau du 2-cycle lorsque le second sommet apparaît exactement au dernier temps visible et que son successeur n'est pas fourni. Cette étape et la conformité à la définition primaire de V19 restent à relire. Le statut général du pilote est indéterminé. Les statuts archivés restent inchangés.
