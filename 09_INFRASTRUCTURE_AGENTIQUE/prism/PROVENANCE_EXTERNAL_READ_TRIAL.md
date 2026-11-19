# Comparaison sur journaux externes — 14 novembre 2026

Référence `3c5197c953361c5e5c08e54e4a3bafe7ad49c3be`. Collecte des journaux via GitHub en lecture autorisée. Le pilote local utilise select_verdict de la PR #80 et choisit le parseur BuildKit lorsqu'un marqueur d'exécution cp -av est présent. Sinon il recherche une commande de liaison Ninja pour la sortie exacte. Le fixe exécute les mêmes parseurs (Bash, BuildKit, liaison) sur la même pièce et rend un verdict si les verdicts déterminés s'accordent. Un extrait est donné à chaque méthode, à budget d'une lecture. Le choix des sorties et la réduction des journaux sont manuels. Aucun libellé attendu n'est fourni aux fonctions. Le parseur de liaison est écrit pour cet essai après observation du format, donc l'essai est rétrospectif et ne constitue pas un holdout aveugle pour son auteur.

| Job et pièce | Omega | Fixe | Lectures par méthode |
|---|---|---|---|
| [K3s Windows](https://github.com/k3s-io/k3s/actions/runs/43477410364/job/132064733875), bloc BuildKit #22 | copie | copie | 1 |
| [curl BoringSSL](https://github.com/curl/curl/actions/runs/43478769616/job/132069490568), ligne de liaison de src/curl et ligne d'installation | recalcul | recalcul | 1 |
| [curl AWS-LC](https://github.com/curl/curl/actions/runs/43478769616/job/132069490874), ligne d'installation de bin/curl seule | indéterminé | indéterminé | 1 |

Le [script K3s épinglé](https://github.com/k3s-io/k3s/blob/a3ac0b54d81269a3f75f1fc2ca8af257a6b04b08/scripts/package-cli) corrobore la copie locale. Le [CMakeLists épinglé](https://github.com/curl/curl/blob/ba36564e1bb47596ac442573555543af68d06ae4/src/CMakeLists.txt) corrobore la construction de la cible curl. L'essai ne compare pas les octets des produits. Le dossier sans trace est un extrait délibérément limité d'un job distinct, et le verdict porte seulement sur les pièces fournies.

Parité sur les trois cas et 24 tests locaux réussis. Aucun changement du routeur de référence. Les extraits n'ont pas été utilisés pour entraîner un candidat. Sortie du relevé local (identifiants a, b, c dans l'ordre du tableau, SHA-256 UTF-8, LF entre les lignes et sans LF final) :

```text
a {'verdict': 'copie', 'pieces_lues': ['journal']} copie fc75f0059a858393562d79f74772ab7d8c1c716fe688d7bf8ea666b8cd4b47fb
b {'verdict': 'recalcul', 'pieces_lues': ['journal']} recalcul 6a8770c28c27479b14863187d3127526d182617b96738a6ed2837f2f7f2b4ba6
c {'verdict': 'indéterminé', 'pieces_lues': ['journal']} indéterminé 2012e5593914ff41a6cdb19a880baad1f0da2f57dc7d5cae204c0f1100d8315f
```
