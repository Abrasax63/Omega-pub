# Contrat de mémoire scientifique partagée

**Version :** 0.1 — **Statut :** proposition non implémentée

## 1. Les trois espaces de connaissance

Le référentiel expose trois espaces logiques. Ils peuvent être physiquement stockés dans plusieurs systèmes, mais leur séparation doit être préservée dans les API, les index et les interfaces.

### A. Mémoire interne certifiée

Contient uniquement les résultats dont le statut et le dossier de validation sont explicitement établis. Chaque entrée est identifiée par un ID stable et une version scientifique. Une correction crée une nouvelle version ou un événement de révision ; elle n'efface pas silencieusement l'état antérieur.

### B. Mémoire interne expérimentale

Contient les hypothèses, explorations, calculs exploratoires, scripts, rapports d'agents, objections, contre-exemples candidats et résultats non résolus. Un résultat peut être utile sans être certifié. Son caractère expérimental doit rester visible dans toute restitution.

### C. Mémoire externe

Contient des références à des articles, livres, dépôts, bases de données, logiciels et résultats publiés hors du projet. Une source externe doit conserver son identité bibliographique, son URL/DOI/identifiant pérenne, sa date de consultation et, lorsque possible, une copie ou empreinte de la version consultée, sous réserve des droits.

**Règle :** une source externe n'est pas une connaissance interne certifiée. Une affirmation expérimentale ne devient pas certifiée parce qu'elle est répétée dans une publication ou par un agent. Les liens entre espaces sont explicites et typés.

## 2. Un paquet de contexte par mission

Le Context Engine remet à chaque agent un paquet structuré qui contient au minimum :

- identifiant de mission et version du contrat de mission ;
- question exacte, périmètre, contraintes et critères de réussite ;
- état de recherche antérieur et verrou actif, s'il existe ;
- résultats pertinents avec ID, version, statut scientifique et statut de publication ;
- définitions, hypothèses et dépendances nécessaires ;
- contre-exemples, objections et tentatives précédentes pertinentes ;
- expériences, données, programmes et rapports associés ;
- références externes avec emplacement précis et date de consultation ;
- lacunes connues et éléments non retrouvés ;
- règles de confidentialité et droits de lecture ;
- empreinte du paquet de contexte et date de constitution.

Chaque élément doit porter son espace épistémique. Il est interdit de livrer une liste de textes aplatis qui ferait disparaître leurs statuts et leurs provenances.

## 3. Auto-référence : citation et résolution

Un agent peut citer :
- une fiche de résultat par son ID et sa version ;
- une section ou un passage précis d'un document ;
- une exécution par son ID de run et son manifeste ;
- un artefact d'un autre agent par son ID, sa version et son statut ;
- une source externe par son identifiant bibliographique et son emplacement.

Une citation à un artefact d'agent doit permettre de remonter à son paquet de contexte, à ses sources et aux artefacts antérieurs dont il dépend. Une citation sans source racine identifiable est marquée comme provenance incomplète.

La citation d'un agent précédent n'est pas une preuve indépendante. Si deux agents utilisent le même résultat intermédiaire, leurs travaux sont dépendants pour ce point, même s'ils raisonnent séparément ensuite.

## 4. Droits de lecture et d'écriture

| Acteur | Lire certifié | Lire expérimental | Lire externe | Proposer | Promouvoir en certifié |
|---|---:|---:|---:|---:|---:|
| Agent de recherche | Oui, selon droits | Oui, selon droits | Oui, selon droits | Oui | Non |
| Agent réfutateur | Oui, selon droits | Oui, selon droits | Oui, selon droits | Objections / contre-exemples | Non |
| Agent formaliste | Oui, selon droits | Oui, selon droits | Oui, selon droits | Preuves / formalisation | Non |
| Agent computationnel | Oui, selon droits | Oui, selon droits | Oui, selon droits | Scripts / sorties / certificats | Non |
| Validateur RAVI-2 | Oui | Oui | Oui | Verdict documenté | Selon le processus RAVI-2, jamais par automatisme |
| Administrateur du dépôt | Selon droits | Selon droits | Selon droits | Gestion documentaire | Ne modifie pas un statut scientifique sans dossier de validation |

Les agents ne reçoivent jamais de droit d'écriture direct sur la mémoire certifiée. Ils déposent dans une zone de propositions. Les changements au dépôt GitHub passent par une branche et une Pull Request, sauf procédure de maintenance explicitement autorisée.

## 5. Prévention des boucles et de la contamination circulaire

- Un graphe de provenance doit signaler les cycles de dépendance.
- Une chaîne de citations qui revient à son point de départ ne crée aucune preuve nouvelle.
- Plusieurs agents partageant le même modèle, prompt, données, code ou raisonnement source ne sont pas automatiquement indépendants.
- L'indépendance doit être qualifiée par dimensions : source, méthode, implémentation, environnement, agent et revue.
- Le nombre d'agents, de votes ou de répétitions n'est jamais un critère de certification.
- Les résultats historiques réfutés ou corrigés restent consultables avec leur statut et la raison de leur déclassement.

## 6. Conservation et évolution

Les événements de recherche sont append-only dans le journal logique : une correction ajoute un nouvel événement qui référence l'événement corrigé. Les artefacts volumineux peuvent être stockés séparément, avec URI, version et empreinte cryptographique.

Une suppression légalement ou opérationnellement nécessaire doit être tracée comme telle sans conserver de données sensibles supprimées dans les journaux. Les contenus privés ne sont jamais copiés dans le dépôt public par défaut.
