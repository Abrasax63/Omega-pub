# Pilote Omega — filtrage à la borne arithmétique

11 novembre 2026. Deux sessions isolées, même dossier, mêmes outils et un appel de calcul maximum. La session guidée a reçu la consigne supplémentaire de chercher une condition nécessaire provenant du dernier défaut avant d’énumérer. Le temps et les tokens n'ont pas été mesurés.

## Résultats mathématiques

Pour D={2,8} et D={4,8}, la borne vaut 12 et impose T=(1,2,0,0,3,4,5,6,7,8,9,10) à renommage près. Le premier spectre est réalisé à la borne par la coloration 001000110001 dans l’ordre 0,…,11. Le second est exclu à cette taille. Le parcours de référence fixe la couleur de l’état 0 et conserve les 1 536 colorations à cycle bicolore. Il retrouve deux colorations de spectre {2,8} et aucune de spectre {4,8}. Les relations sont périodiques de période 3 dès h=9, ce qui rend le contrôle jusqu’à h=11 exhaustif.

## Comparatif

Les deux sessions donnent les deux bons verdicts. Le bras direct rapporte 1 792 colorations parcourues par cible, dont 256 cycles monochromes éliminés ensuite. Il a corrigé une première description imprécise de sa normalisation. Le bras guidé a d’abord fixé la couleur 1 au sommet minoritaire sur le cycle. Comme la rotation à h=8 est non triviale, le cycle fournit déjà (0,0), (0,1) et (1,0). L’unique défaut possible en h=8 est donc l’absence de (1,1). Le filtre teste si un état de couleur 1 retrouve cette couleur après huit pas. Sur les 1 536 colorations normalisées, 208 passent le filtre, soit 48, 64 et 96 selon la position du sommet minoritaire. Ces 208 reçoivent le contrôle complet, partagé entre les deux cibles. Le nombre a été vérifié séparément.

Ce pilote observe une réduction du nombre de dossiers envoyés au contrôle complet, sur un graphe et deux cibles. Les dénominateurs et les méthodes de parcours diffèrent, et le temps total n'a pas été mesuré. Le résultat ne mesure pas un avantage général d’Omega ni du RCE.