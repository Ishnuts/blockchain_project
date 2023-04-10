# blockchain_project

Ce programme permet de simuler un réseau de mineurs et de wallet minant des blocs et effectuant des transactions

## Contenu

- [Projet_Blockchain](#projet_blockchain)
  - [Contenu](#contenu)
  - [Get started](#get-started)
    - [Conditions préalables](#conditions-préalables)
    - [Utilisation](#utilisation)
  - [Construit avec](#construit-avec)
  - [Auteur](#auteur)

## Get started

Ces intructions vous permettront d'obtenir une copie du projet de Blockchain opérationnelle sur votre machine pour pouvoir l'éxécuter sans problèmes.
Un simple _git clone_ du répository vous permettra de récupérer le fichier necessaire.

### Conditions préalables

Avant d'éxécuter le script il y a des conditions préalables à respecter:

1. Posséder Python3 (version utilisée pour le développement 3.11.2)                       Un lien du site officiel pour pouvoir le télécharger : https://www.python.org/downloads/

2. Installer les librairies nécessaires à l'éxécution du script:

```
socket json threading 
time hashlib argparse
```
S'il ne sont pas installer sur votre machine voici la commande permettant de les installer:

```
$pip3 install socket json threading time hashlib argparse
```

### Utilisation

L'utilisation du script est assez simple, mais __ATTENTION__ vous aurez vous besoin de __2 Terminals__ pour lancer le script:

1. Le premier terminal vous permettra de lancer l'éxécution pour la simulation du réseaux de mineurs(P2P) (partie maillage et broadcast),du minage de blocks par ces derniers, ainsi que l'ajout des blocks validé à la blockchain (partie proof of work).

2. Le deuxième terminal vous permettra d'acommplir 2 taches distinctes dans le flux d'affichage du premier terminal:
  1. L'envoie d'une transaction à un mineur par un wallet qui s'affichera 
  2. L'affichage de l'état actuel de la blockchain (qui continue d'etre minée) par un mineur

__ATTENTION IMPORTANT__: Toujours lancé la terminal 1. (celui qui simule le réseau P2P) dans un premier temps , puis dans un second temps lancé le terminal 2.(il est conseillé d'attendre un petit moment que les blocks soit minés (quelques secondes)).

Voci une instance d'exécution possible pour le script sur le premier terminal:
```
$python3 blockchain.py -M miner -p 1000 2000 3000 
```
Et une instance d'éxécution pour sur le deuxième terminal, pour l'envoie d'une transaction:
```
$python3 blockchain.py -M wallet -p 1000 -wa 0x0002 -d 0x9999 -v 2
```

Et une instance d'éxécution pour sur le deuxième terminal, pour l'affichage de l'état actuel de la blockchain:
```
$python3 blockchain.py -M print -p 2000
```


## Construit avec

## Auteur

* **Tony ABEMONTY**