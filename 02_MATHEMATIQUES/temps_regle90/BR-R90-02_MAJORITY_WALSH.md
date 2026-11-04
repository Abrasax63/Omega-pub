# BR-R90-02 — Uniformité Majority–Walsh avant repliement cyclique

- **Identifiant source :** BR-R90-02
- **Version publiée :** 0.1 (transfert documentaire)
- **Domaine :** Mathématiques / dynamique linéaire sur corps fini et observation
- **Statut scientifique enregistré dans la fiche source :** DÉMONTRÉ et reproduit dans l'audit indiqué
- **Statut de publication :** EXPÉRIMENTAL — preuve détaillée et audit source non encore joints à ce dépôt
- **Source documentaire :** bibliothèque de recherche interne, fiche `BR-R90-02_MAJORITY_WALSH.md`
- **Audit source cité par la fiche :** `/Recherche/02_PROGRAMMES_ACTIFS/Temps_Regle90/AUDIT_TEMPS_REGLE90_2026-08-22.md`, section 3

## 1. Domaine

Règle 90 sur un cycle de taille (N), observation locale Majority de trois bits, mot observé (W_h) de longueur (h+1), états initiaux uniformes.

## 2. Énoncé

Si

[
N\geq 2h+3,
]

alors le mot observé est exactement uniforme et

[
H(W_h)=H_2(W_h)=h+1.
]

## 3. Mécanisme de preuve indiqué par la fiche source

La décomposition de Fourier–Walsh de Majority réduit chaque coefficient joint non trivial à un polynôme de Laurent non nul. Son support reste dans ([-h-1,h+1]). La condition (N\geq 2h+3) garantit que la réduction modulo (z^N-1) est injective sur ce support ; aucun coefficient non trivial ne survit.

## 4. Limites

La condition est suffisante, pas annoncée comme nécessaire. Hors domaine, l'uniformité peut échouer. Ce résultat ne prouve ni une fermeture locale de l'observation Majority ni une flèche du temps.

## 5. Éléments de preuve et vérification disponibles

La fiche source renvoie à l'audit indiqué ci-dessus, mais le texte intégral de cet audit n'a pas encore été transféré dans le dépôt public. La preuve est donc décrite ici au niveau de son mécanisme, sans prétendre que le dossier public contient encore tous les détails nécessaires à une reproduction indépendante.

**Conséquence éditoriale :** le statut scientifique DÉMONTRÉ est celui porté par la fiche source interne. Le statut de publication reste EXPÉRIMENTAL tant que la preuve détaillée, ses hypothèses complètes et le protocole de reproduction ne sont pas disponibles publiquement.

## 6. Dépendances

Aucune dépendance formelle n'est déclarée dans la fiche source transférée.

## 7. Historique

- 0.1 — Transfert fidèle de la fiche source vers Omega-pub ; aucune nouvelle preuve ni exécution n'est revendiquée.
