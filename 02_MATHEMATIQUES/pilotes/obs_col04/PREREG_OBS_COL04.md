# OBS-COL-04 — Pré-enregistrement expérimental (2026-11-15)
Statut : protocole **avant implémentation/tests** de ce pilote. Branche séparée basée sur PR #40 ; PR #86 non modifiée. Aucune modification de `main`, aucun secret ou API.

## Question falsifiable
Un pilote composé de générateurs de modèles, du vrai planificateur de décisions Omega P1 / PR #23, du garde-fou consultatif PR #40 et du coefficient Walsh déjà présent dans PR #86 peut-il, sur des transitions partielles, sélectionner des expériences qui réfutent un invariant apparemment conservé ? Quels cas restent indéterminés, sans confondre vérification relative à un catalogue avec loi universelle ?

## Univers synthétique gelé
- Trois bits : états 0..7. Actions `pulse` et `bind`.
- Modèles `(selector, mask0, mask1, bind_mask)` ; `pulse` applique `mask0` si le bit `selector` vaut 0, sinon `mask1`. `bind` applique `bind_mask`. Transitions = XOR du masque.
- Catalogue **annoncé** de 36 hypothèses : selector dans 0,1,2 ; mask0 dans 3,6 ; mask1 dans 1,2,5 ; bind_mask dans 2,6.
- Six mondes tests publics, figés AVANT code : (2,3,1,6), (2,3,5,6), (1,6,5,2), (1,6,2,2), (0,3,2,6), (0,3,5,6).
- Observations initiales, pour chaque cible : sorties des trois capteurs monobit à l'état 0, sous chacune des deux actions. Le détecteur et le planificateur reçoivent ces sorties et le catalogue **mais pas l'identité de la cible**.
- Probes candidates : états 1..7, action pulse, capteurs de XOR de sous-ensembles non vides de bits (masques 1..7) ; 8 sont présélectionnés selon la séparation des décisions au sein des hypothèses, avec couverture des états. Coûts synthétiques déclarés = 12 unités milli par bit observé ; 3 nouvelles requêtes maximum par épisode.
- Les invariants candidats : tous les masques linéaires GF(2) non nuls qui conservent le XOR sous les transitions fournies. Aucune prétention sur tous les invariants non linéaires.

## Comparateurs
- Pilote : exact `plan_with_variable_horizon` (PR #23 et héritage de branche #40) avec P1 réel, profondeur 2, budget de coût `max_cost_milli=144` ; consulte la réponse réelle du générateur synthétique puis filtre les modèles.
- Comparateur indépendant partiel : oracle combinatoire **une étape** sur les mêmes huit consultations candidates (ne doit pas être décrit comme comparateur optimal sur 2 étapes) ; arrêt avant tout test si toutes les décisions sont identiques.
- Politique fixe à trois consultations et contrôles négatifs identiques, à mesurer si l'implémentation le permet.
- PR #40 : `inspect_observer_evidence` consultatif, `declared_exhaustive=False`, sans prendre son retour pour une certification. PR #86 : réutiliser, sans changer, le calcul Walsh d'un ensemble d'observations.

## Indicateurs et verrous
Enregistrer hypothèses survivantes, invariant provisoire initial, invariant robuste relativement au catalogue après probes, vrai invariant **seulement post hoc**, contre-exemples, requêtes et coûts hypothétiques, politique P1 effectivement appelée, avis PR40 non certifiant, comparateurs indépendants.
Conditions d'échec : vrai modèle éliminé ; invariant robuste faux ; décision ou coût inventé ; PR23 / PR40 / PR86 non importés effectivement ; code déclarant Omega autonome ou utilisant les réponses cachées comme entrée du planificateur. Un résultat nul ou indéterminé est recevable.
Ne jamais présenter ce corpus synthétique conçu par nous comme holdout extérieur/aveugle, preuve de découverte ouverte, amélioration par rapport à Bayes/VOI exact, ou preuve de logique universelle.
