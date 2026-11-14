# Opérandes cp dans xtrace — 14 novembre 2026

Référence `202774f868dbc8d36b074bee2563b5a433e1926d`. Trois contrôles synthétiques (`cp --version target`, `cp '--help' target`, `cp -r target`) étaient traités comme copies. Le candidat et le comparateur fixe, qui exige deux opérandes non vides sans tiret initial, s'abstiennent. Les deux contrôles distincts `cp source target` et `cp ./--help target` confirment dans les trois versions. Les textes analysés commencent par `+ `. SHA-256 UTF-8 sans LF final, dans l'ordre :

- 22d79a5d65a5a188427010aa25d3af78ae51a4cfa5443adad86fe9de7286ff06
- d87aacbf3d84392490250a7f509dc421f3a2009ca5a9ed27d39aeaffe9d2ba28
- 043eeb4775cbc2b4eb5330fac1d15987d4e0e1024ba91e349a0b61a562a0228e
- 4bb456c39fc9f690d6a345ba3c4892030865eaf8cc754bc581be2b782b3b47da
- 4cdda2fd3bfb71a373ff335fde48c12cbd20c72373e8d5845e331fce4d983fc8

24 tests locaux passent. La recherche de workflow externe avec xtrace cp et preuve séparée n'a donné aucun résultat admissible. Correctif retenu pour les fausses confirmations synthétiques. Pas de gain externe ni d'apprentissage sur traces annotées.
