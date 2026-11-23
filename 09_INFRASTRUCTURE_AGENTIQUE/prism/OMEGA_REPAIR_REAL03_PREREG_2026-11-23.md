# OMEGA-REPAIR-REAL-03 — gel AVANT toute inférence

Date : 2026-11-23. Branche isolée PR #231. **AUCUN nouveau run au moment de ce préenregistrement.** L'expérience REAL-02 du 23 novembre a admis la citation et la signature «equivalence relation» mais rejeté l'exemple positif (boucle manquante sur c). Ce constat sert UNIQUEMENT de motivation. Ne pas réutiliser cette fiche, cet exemple, ou les questions REAL-02 comme cas de test.

## Question falsifiable

Un modèle local sait-il, sur des **relations nouvelles qu'il construit lui-même**, corriger une erreur après réception d'un **témoin exact de violation**, sans qu'on lui fournisse une relation corrigée ? Une simple nouvelle génération sans témoin suffit-elle aussi ? C'est un test borné de la correction guidée, **pas** une démonstration d'acquisition de connaissances, de nouvelle théorie, de mémorisation persistante ni d'amélioration des poids.

## Cohorte entièrement fixée avant exécution

Quatre tâches inédites, dans cet ordre et sans remplacement post-hoc :
- T1 `partial_order` sur `p,q,r,s` : réflexive, antisymétrique, transitive ;
- T2 `symmetric` sur `u,v,w,x` ;
- T3 `transitive` sur `k,l,m,n` ;
- T4 `antisymmetric` sur `d,e,f,g`.

Utiliser une formulation en langage naturel des propriétés, référencée au livre source d'Oscar Levin (*Discrete Mathematics: An Open Introduction*, 4e édition, CC BY-NC-SA 4.0), version amont figée `1a2005c6797bec10289f09e706f81c6c4b809a52`, fichier `source/sec_gt-relations.ptx` (blob Git `75bebda318694bb4712d60380b0e183e77f1e757`). Contrairement à REAL-02, on examine ici **les compétences de correction sur des exemples nouveaux**, non l'acquisition autonome depuis une source Web nouvelle. Pas d'information sur les quatre sorties attendues ni d'exemples construits par le chercheur dans les prompts.

Chaque tâche commence par **une** génération du modèle : relation sur les quatre sommets, au moins 2 arêtes hors diagonale, JSON à clé `edges`. Aucune sortie initiale n'est modifiée automatiquement. Pour l'oracle, toute réponse non JSON ou liste invalide est un échec de format, et NON une «erreur mathématique» réparable ; elle reste au dénominateur. Les relations valides sont soumises au `check_axioms` exact d'Omega. Un cas initialement correct **n'est pas soumis à une fausse faute** et compte comme succès initial, pas comme correction.

## Deux bras appariés sur la MÊME sortie initiale (si elle viole la définition)

W = **témoin exact** : « le candidat viole [nom de propriété], témoin [valeurs] » provenant de `check_axioms`, et la liste initiale, **sans fournir de nouvel ensemble d'arêtes ni instruction locale d'ajouter/supprimer une arête**. Exposer un seul premier échec dans l'ordre immuable `reflexive, symmetric, antisymmetric, transitive`, sans aucun autre indice.

G = **retour générique** (contrôle négatif) : « le candidat viole au moins une propriété requise, mais les détails sont masqués » + même sortie initiale ; aucune propriété, témoin ou suggestion de correction. Même instruction de réparer, une seule tentative. Les deux bras repartent du même état initial ; pas d'historique W communiqué à G ni inversement. Ordre de génération W/G alterné sur les tâches `W,G;G,W;W,G;G,W`.

Plafond **1** tentative de réparation par bras, aucune régénération si mauvais JSON ou erreur. Comparabilité : même modèle, fichier GGUF SHA-256 `9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94` ; `llama.cpp b12633` ; CPU ; `temperature=0`, `seed=9123`, `max_tokens=260` par génération, JSON mode. Pour éviter qu'un témoin plus long soit pris pour un gain de calcul, les prompts de réparation doivent être égalisés **avant appels** à ±5 % en tokens d'entrée via remplissage administratif neutre; en cas d'impossibilité le statut causal devient INDÉTERMINÉ, et les données restent conservées. L'initial généré n'est jamais rééchantillonné.

## Vérification et métriques gelées

Oracle : relation décodée sur exactement quatre sommets, aucune arête dupliquée ni sommet extérieur, minimum deux arêtes hors diagonale (pour éviter les solutions dégénérées), propriétés mathématiques évaluées sur la relation complète. Pour T1, les trois axiomes sont nécessaires simultanément. Sur chaque réparation : sortie JSON admissible, toutes les propriétés exigées, arêtes modifiées par rapport à l'initial (sinon pas de réparation), nombre d'arêtes modifiées, conservation du critère non-trivial. Une relation correctrice peut être entièrement différente : signaler ce fait; ne pas qualifier de «correction minimale» sans le prouver.

Compteurs : 4 générations initiales ; E = nombre de relations initiales bien formées mais mathématiquement erronées ; E_brut = erreurs incluant format. Taux initial exact /4 ; erreurs détectées par oracle /4 ; corrections correctes W/E et G/E ; W-G en nombre de cas ; erreurs mathématiques silencieuses (0 car contrôle oracle exact dans son domaine, sous réserve de conformité de l'oracle), JSON invalides, abstentions, tokens, durées, nombre d'appels et SHA de tous les prompts/réponses. Reporter également 0<E<2 comme manque de puissance, pas comme absence générale de capacité.

**Critère de succès ponctuel préenregistré** : E≥2, W corrige au moins 2 erreurs, W dépasse G d'au moins 2 corrections, **aucun** format invalide après témoin et comparabilité ±5 % atteinte. Aucun test statistique positif possible avec quatre tâches. Si E≥2 et W ne dépasse pas G de deux, critère de supériorité du témoin **NON SATISFAIT sur ce pilote**. Si E<2, si erreur de budget, de source, de format ou de transport, **INDÉTERMINÉ** pour l'hypothèse comparative. Une correction réussie avec W mais également réussie avec G établit la possibilité de réparer, pas l'utilité différentielle du témoin.

## Intégrité, coût et arrêt

Au maximum 4 initiaux + 8 réparations = 12 générations, un seul run de modèle réel. Pas d'API payante. Aucun workflow programmé ; aucun changement de `main`, aucune promotion en mémoire certifiée, aucune modification des cycles Omega. Les modèles peuvent être rappelés sur GitHub Actions Linux/CPU sans GPU. Les validations hors ligne précèdent l'inférence. Le système conserve JSON d'essais, prompts envoyés (et SHA), sorties brutes, résultats des vérificateurs et tokens. Si une erreur déterminante est révélée après un run, ne pas corriger puis relancer sur cette cohorte pour prétendre à une preuve indépendante ; corriger dans un nouveau protocole/cohorte.

**Note méthodologique :** un témoin exact peut parfois révéler directement l'arête manquante (réflexivité), même sans donner l'ensemble réparé. Mesurer cette facilitation, ne pas l'appeler compréhension profonde. Le choix de quatre tâches et du même manuel partiellement utilisé en REAL-02 limite la généralité.
