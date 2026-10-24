# PT-StandAssign-Vatsim
Projeto para o desenvolvimento de um sistema de atribuição automática de stands ao tráfego aéreo em fase de aproximação.

Este projeto é um projeto pessoal, que tem por objetivo eu aprender no desenvolvimento de software e utilizar este tempo gasto no estudo para contruibuir para organisações como neste caso VATSIM Portugal.















# Plan par étapes : stands automatiques sur Porto (LPPR)

Les durées sont indicatives, à adapter à votre rythme.

## Étape 1 : Préparer l'environnement (1 jour)
- <mark>Installez Python et VS Code.</mark>
- <mark>Demandez votre code Hoppie.</mark>
- <mark>Créez un dossier de projet, avec Git si vous voulez garder l'historique.</mark>
- <mark>Ecrire un petit programme qui télécharge le flux VATSIM et affiche les pilotes qui arrivent à LPPR.</mark>
- Alterar no vatsim_lppr_loop.py o REFRESH_RATE de 15s para 300s.

## Étape 2 : Construire la base de stands de Porto (3 à 7 jours)
C'est la partie la plus longue, mais la plus importante.
- <mark>Récupérez la liste des stands dans l'AIP Portugal (carte de stationnement de LPPR).</mark>
- <mark>Relevez les coordonnées de chaque stand (OpenStreetMap ou QGIS).</mark>
- <mark>Pour chaque stand, notez la catégorie max (L, M, H) et la compagnie préférée éventuelle.</mark>
- <mark>Rangez tout dans un CSV, et vérifiez-le visuellement sur une carte.</mark>

## Étape 3 : Déterminer la catégorie des avions (1 jour)
- <mark>Faites une table type OACI vers L, M ou H.</mark>
- Choisissez ce qui se passe avec un type inconnu (par exemple le classer en moyen, ou ne rien envoyer).
- Complétez la table au fil des tests.

## Étape 4 : Détecter les contrôleurs en ligne (1 jour)
- Lisez la liste des contrôleurs du flux VATSIM.
- <mark>Considérez que le système est actif s'il n'y a aucun contrôleur `LPPR_` de type Delivery, Ground ou Tower.</mark>
- Ajoutez un délai de 2 à 3 cycles avant tout changement d'état, pour éviter les allers-retours.

## Étape 5 : Écrire le moteur d'attribution (3 à 5 jours)
- Sélectionnez les avions en approche vers LPPR.
- Choisissez le stand : compatible avec la catégorie, libre, avec priorité à la compagnie.
- Gardez en mémoire les stands réservés et libérez-les quand le pilote se déconnecte.
- Gérez les cas limites : plus de stand libre, stand devenu occupé avant l'arrivée.
- Dans un premier temps, affichez les attributions à l'écran sans rien envoyer.

## Étape 6 : Brancher l'envoi Hoppie (1 à 2 jours)
- Envoyez le télex une seule fois par avion.
- Gérez les erreurs d'envoi (le réseau Hoppie n'est pas toujours fiable).
- Écrivez un journal de tout ce qui est envoyé, pour comprendre les décisions.

## Étape 7 : Tester (1 à 2 semaines)
- Testez avec vos propres vols vers LPPR, avec plusieurs types d'avion.
- Demandez à quelques amis de voler vers Porto pour voir le système en situation réelle.
- Vérifiez : stands cohérents, pas de doublons, mise en veille quand un contrôleur se connecte.

## Étape 8 : Contacter la vACC Portugal (à faire en parallèle, dès l'étape 2)
- Présentez le projet et le principe « actif seulement sans ATC ».
- Demandez leurs données de stands et leur avis sur les positions à prendre en compte.
- Demandez leur accord avant toute ouverture au public.

## Étape 9 : Déploiement (selon l'accord)
- Faites tourner le programme en continu (PC, Raspberry Pi ou VPS).
- Annoncez-le aux pilotes, avec un moyen de signaler les problèmes.
- Surveillez les premiers jours, puis corrigez.

## Étape 10 : Extension (plus tard)
- Ajoutez Lisbonne, Faro et Madère en copiant la structure : un CSV par aéroport.
- Si la vACC le souhaite, ajoutez des options (demande de stand par le pilote, affichage pour les contrôleurs).

## Ordre de priorité si vous manquez de temps
Étapes 1, 2, 5 et 6 forment le cœur du projet. L'étape 8 doit commencer tôt, car les réponses de la vACC peuvent changer vos choix.

Je peux aussi mettre ce plan dans un Claude Doc, avec votre précédente réponse sur les outils, si vous voulez le garder sous la main.