# BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01 — Complexite cyclique a deux grands gaps identiques

Statut : DÉMONTRÉ interne, certification interne RAVI-2 de validité. Originalité : INDÉTERMINÉE.

Pour g,delta>=1 et 1<=a<b entiers, P=10^(g-1), W=P^a0^delta P^b0^delta, T=(a+b)g+2delta, la complexite cyclique vaut p(L)=2+min(L-1,g+delta-2)+min(max(L-g,0),(b-1)g)+min(max(L-(a+1)g,0),ag+delta), 1<=L<=T. Les facteurs speciaux sont exactement Z_L pour 1<=L<=g+delta-2, B_L pour g<=L<=bg-1, C_L pour (a+1)g<=L<=(2a+1)g+delta-1. W est primitif et le premier horizon distinguant toutes les phases est max(bg,(2a+1)g+delta).

## Domaine et hypotheses

- g et delta entiers >=1
- a,b entiers avec 1<=a<b
- P=10^(g-1)
- T=(a+b)g+2delta
- facteurs cycliques de W ou facteurs de W infini periodique
- 1<=L<=T

## Preuve et limites

Preuve exhaustive par comparaison des contextes aux deux coupures exceptionnelles avec les coupures ordinaires; lcs=(min(c,j)+1)g-1 si c!=j; cas aligne c=j=a: (2a+1)g+delta-1. Deux algorithmes de controle: 288 familles/6720 longueurs et 1080 familles/40500 longueurs, reproduits depuis le code archive. Revue et calculs internes par le meme assistant; aucune revue humaine, autre modele ou verification formelle. Audit bibliographique cible effectue tardivement, non-conformite de sequence conservee; originalite indeterminee.

La preuve autonome et ses sources sont dans /Recherche/02_PROGRAMMES_ACTIFS/Observabilite/REPRISE_MULTI_GAP_2026-10-20.md. Aucun DEPEND_DE ajoute. Le cas g=delta=1 est deja couvert par la brique SINGLE-GAP apres complement. Le cas a=b est exclu.

Certificat : /Recherche/03_AUDITS_CERTIFICATS/TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json
Controles : /Recherche/04_CODE_DONNEES/TWO_EQUAL_GAPS_CHECKS_2026-10-20.json
Code : /Recherche/04_CODE_DONNEES/two_equal_gap_reproduce_20261020.py