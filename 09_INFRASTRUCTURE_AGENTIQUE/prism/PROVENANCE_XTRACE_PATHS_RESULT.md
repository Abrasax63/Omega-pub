# Normalisation BuildKit — 14 novembre 2026

Référence f630573d6a3b40c9596b102646ff2d8051b9981f, candidat 96845fe6fca5887c86e3cf35941a355d34e56ece et test c5aa3d16eee749cc9d3158eac31ff205a5a0fe0d.

[Journal K3s déjà étudié](https://github.com/k3s-io/k3s/actions/runs/43476757307/job/132062459438), lignes horodatées #22 jointes par LF sans LF final. Sur l'original, référence, candidat et fixe confirment la copie. En ajoutant ./ aux deux chemins du retour verbeux, la référence s'abstient tandis que le candidat et le fixe confirment. Une destination différente donne trois abstentions. Le comparateur fixe exige l'identité des chemins après suppression d'un préfixe ./.

SHA-256 (original, préfixes, autre destination) : bac44f4af39f6fd468e76ec1e3dfac3a33e13a8906b8c7e0e2aa9112472d0801, 1674383ad4724235861dfcca8129585cf6024dda2fb28ece3a8482351619ee9f, 984bc9f0148b0db38d75db419e23fd4aebb6e43e911590e3bee423a5de60a98c.

Les 23 tests locaux passent. Correctif retenu pour le gain d'invariance sur un contrôle synthétique. Aucun workflow inédit admissible n'a été trouvé. Aucun gain externe et aucune synthèse de règle sur des observations annotées.
