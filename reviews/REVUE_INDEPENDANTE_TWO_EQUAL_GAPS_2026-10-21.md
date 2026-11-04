# Revue par deux agents distincts — TWO-EQUAL-GAPS

Date : 21 octobre 2026. Résultat : BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01.

## Synthèse

Deux agents IA distincts de l'auteur initial ont rendu des avis séparés, l'un sur la preuve, l'autre sur les antériorités. Ils avaient accès à la dérivation et au contexte : il ne s'agit ni d'une revue aveugle, ni d'une évaluation humaine, ni d'une vérification formelle. L'identité exacte du modèle n'étant pas fournie, ne pas parler de deux modèles différents.

Validité : VALID_INTERNAL après relecture analytique. Originalité : INDÉTERMINÉE maintenue. Aucune nouvelle brique, aucun changement de l'énoncé et aucun rollback justifié par ces avis. La brique est déjà intégrée au noyau comme DÉMONTRÉ interne ; les formulations orales « sans promotion » après cette intégration étaient inexactes et sont corrigées ici.

## Revue contradictoire de la preuve

L'évaluateur a repris la preuve depuis les occurrences aux coupures, sans considérer le statut du certificat comme prémisse. Aucune campagne d'énumération supplémentaire n'a été menée.

1. Un facteur spécial non nul se termine nécessairement par g−1 zéros. S'il se terminait par g+δ−1 zéros, son extension par 0 dépasserait la plus longue plage de zéros.
2. Ses occurrences suivies de 0 se terminent aux deux coupures exceptionnelles E_a et E_b. Celles suivies de 1 sont aux coupures ordinaires O_{r,j}, 1≤j<r, r∈{a,b}. Ces possibilités sont exhaustives.
3. Pour c≠j, les deux contextes ont exactement (min(c,j)+1)g−1 symboles de suffixe commun. Ils partagent min(c,j) blocs P puis g−1 zéros ; le caractère précédent compare un zéro ajouté à un 1. L'unique comparaison alignée possible est c=j=a, dans la plage longue b. Elle fournit (2a+1)g+δ−1 symboles de suffixe commun.
4. Les suffixes de E_b donnent exactement B_L pour g≤L≤bg−1. Les suffixes de E_a coïncident avec B_L jusqu'à (a+1)g−1 puis donnent la famille distincte C_L jusqu'à (2a+1)g+δ−1. Les facteurs entièrement nuls donnent Z_L jusqu'à g+δ−2. La somme des trois indicatrices restitue la formule.

Les frontières g=1, δ arbitrairement grand, a=1 et b=a+1 sont couvertes par ces comparaisons. La coupure O_{b,a} existe toujours. Le cas a=b est exclu à juste titre : W=(P^a0^δ)^2.

Primitivité : une répétition non triviale doit répéter les deux grands gaps ; sa multiplicité divise 2. Une multiplicité 2 imposerait a=b. Les trois plateaux de p(L) somment à T, donc leur saturation donne L_phase=max(bg,(2a+1)g+δ). Ce seuil est inférieur à T puisque T−bg=ag+2δ>0 et T−((2a+1)g+δ)=(b−a−1)g+δ>0.

Amendement rédactionnel conseillé : remplacer « les blocs maximaux de zéros ont longueurs g−1 et h−1 » par « les gaps produisent g−1 ou h−1 zéros ; les blocs non vides ont les longueurs positives correspondantes ». Pour g=1, parler d'un bloc maximal de longueur zéro est impropre. Cela ne change ni la preuve ni le résultat. La preuve historique est conservée sans modification d'octets afin de préserver sa provenance et ses empreintes ; cet amendement est consigné dans le présent addendum.

## Audit bibliographique séparé

Source primaire supplémentaire vérifiée : Anna Frid, Applying a uniform marked morphism to a word, Discrete Mathematics and Theoretical Computer Science 3 (1999), 125–140, DOI 10.46298/dmtcs.255.
https://dmtcs.episciences.org/255/pdf

L'évaluateur a lu les définitions p.126 et les théorèmes 1–2 pp.129–130. Le coordinateur a également ouvert la source primaire et vérifié les définitions et passages des théorèmes. Frid donne des relations exactes de transport de complexité sous morphismes uniformes marqués et circulaires, au-delà d'un seuil de synchronisation. Le théorème 1 comprend aussi une identité ensembliste sous uniformité sans marquage ; extraire une cardinalité exige alors de contrôler les collisions.

Notre morphisme est φ(1)=10^{g−1}, φ(0)=0^δ. Il n'est uniforme que si δ=g. Pour g>1, les deux images finissent par 0, donc il n'est pas marqué au sens de Frid. Pour g=1, l'uniformité impose δ=1 : c'est le sous-cas déjà ramené au single-gap par complémentation. Ces théorèmes ne subsument donc pas directement la formule générale sous la représentation vérifiée. Cela n'exclut pas une autre représentation, une adaptation du théorème ou une publication plus générale.

Correction bibliographique : il serait faux de dire que les résultats morphiques existants ne donnent que des bornes. Le théorème de Lustig consulté précédemment donne des bornes ; Frid donne un transport exact sous hypothèses plus fortes. Aucune antériorité exacte pour toute notre famille n'a été attestée par cette recherche bornée, et aucune nouveauté n'est attestée non plus.

## Décision et portée

- Maintenir DÉMONTRÉ interne pour la validité du domaine déclaré.
- Maintenir INDÉTERMINÉ pour l'originalité. La revue de preuve ne peut pas lever une incertitude de priorité bibliographique.
- Revue analytique par agent distinct désormais disponible ; aucune validation humaine ou formelle.
- Conserver la non-conformité antérieure : l'audit ciblé initial était tardif. La revue actuelle ne réécrit pas cette chronologie.
- Ne pas rouvrir automatiquement une série de nouveaux tests : les deux expériences initiales restent le budget exécuté ; la présente revue est analytique et documentaire.
- Le certificat initial décrit l'état au moment de sa création, sans agent distinct ; cet addendum documente la revue ultérieure. Aucun octet de ce certificat, de la preuve ou des bases n'est remplacé dans cette opération ; leurs empreintes demeurent valables.

Sources internes : REPRISE_MULTI_GAP_2026-10-20.md ; BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01_BRIQUE.md ; TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json ; AUDIT_BIBLIO_TWO_EQUAL_GAPS_2026-10-21.md. Deux rapports d'agents rendus au coordinateur pendant cette conversation ; aucun courriel ni contact externe envoyé.