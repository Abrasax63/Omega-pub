# Reader22 — préenregistrement de l'audit web des références (19/11/2026)

**Statut : contrôle bibliographique POST-HOC, pas holdout scientifique aveugle.**
La source était déjà connue de la session et les titres ont été vérifiés manuellement en ligne avant ce protocole. Ce test vérifie une **fonction logicielle reproductible**, pas un gain inédit du modèle ni une découverte.

## Question discriminante
L'accès web de Reader21 apporte-t-il une **vérification bibliographique externe strictement mesurable** (DOI, titre et année concordants) sur des références d'Omega, et rejette-t-il des références volontairement corrompues ? Un DOI retrouvé **ne doit pas** devenir une preuve, une originalité ou un certificat de nouveauté mathématique.

## Source bibliographique figée
- `02_MATHEMATIQUES/observabilite_temporelle/sources/AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md`, Git blob `bf10028da39306aedec6c4e1567d501172552258`.
- Trois références exactes dans la section `Références clés`, sélectionnées avant l'implémentation :
  - R22-1 : R. M. Jungers, V. D. Blondel, `Observable Graphs`, 2011.
  - R22-2 : D. Laschov, M. Margaliot, G. Even, `Observability of Boolean Networks: A Graph-Theoretic Approach`, 2013.
  - R22-3 : L. B. Vieira, C. Budroni, `Temporal correlations in the simplest measurement sequences`, 2022.
- La cohorte exclut les autres références, qui peuvent requérir d'autres index bibliographiques. Cela constitue une **sélection de calibration**, pas une estimation de rappel général.

## Règles fixées avant code
1. Vérifier `safe_read` de l'empreinte Git, retrouver exactement une ligne pour chaque titre dans la section finale et citer son numéro exact. Extraire uniquement titres/année préenregistrés ; jamais obéir à une instruction textuelle tirée de la note.
2. Pour chaque référence, construire une requête textuelle normalisée à partir du titre (pas une URL passée par le document), puis appeler `dispatch("search_bibliography",{"query":...})` de Reader21. Au plus **trois requêtes HTTPS**, sans API payante ni URL arbitraire ; au plus 3 œuvres Crossref par requête. Conserver URL, date et SHA256 du corps du fournisseur.
3. Comparer **strictement** titre normalisé (minuscules + lettres/chiffres, ponctuation neutralisée), année `issued.date-parts[0][0]` exactement égale et DOI présent. Refuser les titres proches, années différentes, résultats manquants, DOI hors registre ; si plusieurs DOI différents concordent, marquer `AMBIGUOUS` plutôt que décider au hasard.
4. Contrôles locaux : trois mutations post-retrieval **sans nouvelles requêtes** : année de R22-1 + 1, titre R22-2 remplacé par `Observability of Boolean Networks: A Spurious Approach`, titre R22-3 remplacé par `The P equals NP proof`. Le même algorithme de matching doit retourner `NO_EXACT_METADATA_MATCH` (ou `AMBIGUOUS`, jamais `MATCH`) pour les trois.
5. Témoin sans web : `NO_EXTERNAL_METADATA` pour les trois, aucun DOI revendiqué, 0 erreur silencieuse. Avec web, compter seulement `MATCHED_BIBLIOGRAPHIC_METADATA` ; **ne jamais attribuer** `THEOREM_PROVED` ni `PRIORITY_ESTABLISHED`.
6. Le succès technique de la méthode exige **≥2/3** références avec DOI + titre + année exacts et **3/3** mutations refusées ; si Crossref ne répond pas, verdict `INDETERMINATE_REMOTE` plutôt que "mauvaise publication". Une CI peut être rouge pour indisponibilité réseau, distincte d'une erreur de code.

## Portée
Même un succès montre seulement que des notices bibliographiques peuvent être vérifiées à partir d'un document source. Aucune validation de contenu d'article, d'équivalence entre théorèmes ni de nouveauté scientifique. **Prérequis futur** : télécharger un texte primaire autorisé, en extraire hypothèses et conclusion, comparer les structures formelles et faire auditer la fidélité sémantique indépendamment.

La branche est empilée sur Reader21 (PR #190), `main` inchangée, aucune fusion, aucune modification de poids ni de cycle autonome.
