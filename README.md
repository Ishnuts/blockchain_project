# blockchain_project

Ce programme permet de simuler un réseau de mineurs et de wallet minant des blocs et effectuant des transactions

## Contenu

- [Projet_Blockchain](#projet_blockchain)
  - [Contenu](#contenu)
  - [Get started](#get-started)
    - [Conditions préalables](#conditions-préalables)
    - [Utilisation](#utilisation)
  - [Explication globale](#explication-globale)
  - [Auteur](#auteur)

## Get started

Ces intructions vous permettront d'obtenir une copie du projet de Blockchain opérationnel sur votre machine pour pouvoir l'éxécuter sans problèmes.
Un simple _git clone_ du répository vous permettra de récupérer le fichier necessaire.

### Conditions préalables

Avant d'éxécuter le script il y a des conditions préalables à respecter:

1. Posséder Python3 (version utilisée pour le développement 3.11.2)                       Un lien du site officiel pour pouvoir le télécharger : https://www.python.org/downloads/

2. Installer les librairies nécessaires à l'éxécution du script:

```
socket json threading 
time hashlib argparse
```
Toutes les libraires utilisées sont des built-in modules de python. Il n'y a donc aucun besoin à installer des packages.



### Utilisation

L'utilisation du script est assez simple, mais __ATTENTION__ vous aurez vous besoin de __2 Terminals__ pour lancer le script:

1. Le premier terminal vous permettra de lancer l'éxécution pour la simulation du réseaux de mineurs(P2P) (partie maillage et broadcast),du minage de blocks par ces derniers, ainsi que l'ajout des blocks validé à la blockchain (partie proof of work).

2. Le deuxième terminal vous permettra d'acommplir 2 taches distinctes dans le flux d'affichage du premier terminal:
    - L'envoie d'une transaction à un mineur par un wallet
    - L'affichage de l'état actuel de la blockchain d'un mineur

__ATTENTION IMPORTANT__: Toujours lancer le terminal 1. (celui qui simule le réseau P2P) dans un premier temps , puis dans un second temps lancé le terminal 2.

Voci une instance d'exécution possible pour le script sur le premier terminal:
```
$ python3 blockchain.py --mode miner -p 1000 2000 3000 
```
Cela va lancer un réseau P2P de 3 mineurs ayant pour port 1000, 2000, 3000.

Voici une autre instance d'éxécution pour sur le deuxième terminal, pour l'envoi d'une transaction:
```
$ python3 blockchain.py --mode wallet -p 1000 -wa 0x0002 -d 0x9999 -v 2
```
Cette commande va lancer le script en mode wallet, et va envoyer une transaction au mineur ayant le port 1000. La transaction aura 0x0002 pour sender address, 0x9999 comme destination address et 2 pour valeur.

Enfin, voici une instance d'éxécution pour sur le deuxième terminal:
```
$ python3 blockchain.py --mode print -p 2000
```
Cette commande va afficher dans le premier terminal l'état actuel de la blockchain du mineur ayant pour port 2000.

Le script nécessite la spécification de certains paramètres pour son éxécution, il est conseillé de lire les différents options afin de personnaliser l'éxécution:

* -h, --help            : Affiche l'aide

* -M, --mode            : [Obligatoire] Permet de changer de mode entre [`miner|wallet|print`]

* -a                    : [Facultatif] par défaut: `localhost`
  - Mode miner: Ports des différents mineurs du réseaux par default: 
  - Mode wallet: Port du mineur pour la récéption de la transaction
  - Mode print: Port du mineur pour lequel on affiche l'état de sa blockchain

* -p                    : [Obligatoire]
  - Mode miner: Ports des différents mineurs du réseaux par default: `1000`
  - Mode wallet: Port du mineur pour la récéption de la transaction
  - Mode print: Port du mineur pour lequel on affiche l'état de sa blockchain

* -wa                   : [Mode Wallet Only] Adresse du wallet | par default : `0x00001`

* -d                    : [Mode Wallet Only] Adresse du destinataire de la transaction du wallet | par default : `0x00002`

* -v                    : [Mode Wallet Only] valeur de la transaction | par défaut: `1`

## Explication globale

Lorsque l'on démarre un mineur, on lance la fonction start qui démarre deux threads, l'un pour l'écoute des connexions entrantes et l'autre pour le minage de la blockchain.

La méthode "mine" s'exécute en boucle et crée un nouveau bloc, le mine et l'ajoute à la blockchain. Si la blockchain a été modifiée entre-temps par un autre mineur, la méthode recommence le minage avec un nouveau bloc.

## Auteur

* **Tony ABEMONTY**