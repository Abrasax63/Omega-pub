# OMEGA-BRIDGE-SCOPE-V2 — correction post-hoc de la portée des interprétations
Date : 2026-11-17. Empilée sur PR #151 ; conserver l'expérience v0.1 et son run 44113864866 sans modification.

## Défaut détecté
La fiche historique BR-DESC-01 indique « Dans le cas de référence étudié sur un cycle de longueur première p ». La transcription v0.1 n'énumère que `prime_cycle` et `binary_nonconstant_output` pour ses conclusions, sans demander explicitement `reference_model`. Cela peut promouvoir un résultat quantitatif hors du cas réellement décrit.

## Correction déterministe
Créer un nouveau manifeste VERSIONNÉ, séparé des règles historiques gelées, avec hypothèse `reference_model` sur les trois règles BR-DESC-01. Ne changer ni le moteur générique, ni le corpus du pilote v0.1, ni ses rapports. Le programme lit le manifeste v2 seulement si son empreinte Git exacte est fournie.

## Contrôles distincts
Construire un nouveau petit jeu de demandes v2 : les cas anciens seront rejoués **post-hoc** avec l'hypothèse du modèle de référence explicitée ; les contrôles nouveaux vérifient l'abstention sur un cycle premier de modèle non identifié et sur une entrée qui déclare le résultat intermédiaire mais pas le modèle. Le vérificateur indépendant à énumération doit rester d'accord et les citations doivent rester exactes.

## Interprétation
Il s'agit d'une **réparation de portée**, pas d'une performance ou généralisation nouvelle. Le gold reste manuel et dépend du contrat ; aucune preuve universelle n'est certifiée. CI verte n'autorise pas une fusion automatique.
