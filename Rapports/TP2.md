# TP2 : Suite de la découverte de Docker

Noms des auteurs :  DAUB Justin
Date de réalisation : 10/02/2026

## 1. Les volumes Docker

Documentez les commandes importantes de cette section. 

Lors d'un ```docker run``` :
- -- mount sert à monter le stockage (on met sois le nom du stockage docker, ou le chemin d'accès de l'ordinateur hôte pour le bind mount)
- -- name pour donner un nom au serveur 

Quelles sont les différences entre les deux types de volumes utilisés ici ?  Dans quel cas utiliser l'un plutôt que l'autre? 

Le bind mount connecte directement le container où s’exécute l'image, à l'ordinateur hôte. Dans la source lors du montage du stockage, on a choisis un chemin de l'ordinateur, hôte on a récupérer le chemin du répertoire où l'on exécute la commande de montage. Avec le bind mount les modifications faites sur la machine hôte, sont prises en compte par le container et met à jour le site. 

Le volume docker lui, est une sorte de stockage virtuelle pour docker que les containers peuvent utiliser. C'est un stockage uniquement accessible sur des container, contrairement au bind mount il n'accède pas à un chemin de la machine hôte, mais au stockage qui a été crée. Avec ceci, plusieurs containers peuvent travailler sur le même stockage, ce qui fait qu'on retrouve les mêmes fichiers sur tous les containers utilisant le même volume, comme dans le cas du serveur sur le port 80 et 81 qui utilisent le même volume.

Ainsi, si on souhaite travailler depuis l'ordinateur hôte on privilégie le bind mount, et si on veut des containers avec les mêmes fichiers partagés, on utilisera un volume docker.
## 2. Les réseaux Docker

Documentez les commandes importantes de cette section. 

- ```ip addr``` : (Dans un bash) Afficher l'adresse IP du containeur 
- ```ping``` : (Dans un bash) Envoyer des paquets vers une adresse IP ou un site, pour vérifier la communication vers la cible.
- ```docker create network <nom-network>``` Créer un network nomée (un nouveau réseau docker)

### 2.1. Réseau par défaut

1.  Quelles sont les interfaces réseau et adresses IP de chaque container? Vous pouvez trouvez cette information soit depuis l'hôte avec un ```docker inspect```(cfr TP1), soit depuis le container lui-même.  Note dans ce dernier cas : Si la commande ```ip addr```n'est pas disponible, installez le package ```iproute2```. 

Adresse IP du 1er container (port 80) : 172.17.0.2  
Interface réseau du 1er container (port 80) : eth0

Adresse IP du 2ème container (port 81) : 172.17.0.3
Interface réseau du 2ème container (port 81) : eth0

2. Les containers peuvent-ils se joindre via ```ping``` ? 

Oui les 2 containers, peuvent se joindre, en faisant un ping de l'adresse IP de l'autre container, tous les paquets sont transmis, ce qui signifie qu'ils peuvent se joindre.

3. Les containers ont-ils accès à Internet ? 

Oui ils ont bien accès à internet on fait un ```ping``` vers google.com, et on constate que les paquets sont tous bien reçus ce qui montrer qu'il peuvent accéder à internet. 

4. Est-ce une bonne idée d'utiliser ce réseau par défaut?  Quels en sont les avantages et les inconvénients ?  

En terme de sécurité non ce n'est pas une bonne idée de l'utiliser par défaut, vu que par défaut ils sont tous sur le réseau bridge, n'importe qui peut savoir le nom du réseau et donc éventuellement y accéder. L'avantages, est que il est simple à mettre en place il y a peu de config à faire et il n'est pas nécessaire de créer un autre network. Mais néanmoins en terme de désavantage c'est moins sécurisé c'est le réseau par défaut qui est utilisée, et peut donc être facilement connu des autres. 

### 2.2. Réseaux définis par l'utilisateur 

1. Le nouveau container ajouté sur le réseau ```my-net``` peut-il contacter les deux précédents (liés au réseau bridge par défaut)?  A-t-il accès à Internet?

Ce container ne peut pas contacter les deux précédents, si on ping les deux précédents, il n'y a aucune tranmission de paquet, il ne communiquent pas. Cela est normal car nous nous sommes pas sur le même réseau il est logique qu'il ne puisse pas communiquer avec un autre réseau. 

Néanmoins il a accès à internet, on faisant un ```ping``` vers google.com, il y a bien transmission de paquet ce qui montre qu'il peut accéder à internet, ce qui est normal car tout réseau peut accéder à internet.

2. Quels sont les différences entre ce nouveau réseau et le bridge par défaut?  Quels en sont les avantages et inconvénients ? 

Ici nous avons créer un réseau à part du réseau par défaut du bridge, contrairement à l'autre qui était relié au bridge par défaut. L'avantage est que cette fois-ci c'est plus sécurisé, on est sur un réseau avec un nom personnalisé, on est isolé du reste et du réseau par défaut. Le désavantage est que c'est un peu plus dur a mettre en place il faut créer un nouveau network, et on ne peut plus communiquer avec le réseau par défaut.

## 3. Docker-compose

1. Qu'avez-vous observé lors de cette première expérience avec Docker Compose ?  Faites un court bilan sur base de screenshots. 

Lors de l'exécution de la commande ```docker compose up```, on remarque dans le terminal qu'il y a le nom des 2 conteurs crée d'un coup avec le compose. Il y a toutes les commandes des 2 conteneurs qui sont réunis au même endroit, nous avons crée 2 conteneurs en même temps avec toute leur architecture configuré. 
![Extrait du compose up](/TP2/pictures/compose.png)

On retrouve bien leur volume commun, leur network a eux et leur image. 

**Containers du compose up**
![Containers du compose up](/TP2/pictures/compose-containers.png)

**Network du compose up**
![Network du compose up](/TP2/pictures/compose-networks.png)

**Volume du compose up**
![Volume du compose up](/TP2/pictures/compose-volumes.png)

Avec le même volume partagés par ces 2 conteneurs, il y a bien la même page web modifié sur les 2 ports, et en faisant un ping entre eux, il communiquent sans problèmes tout en utilisant leur nom de containers.

2. Documentez les commandes importantes. 

- ```docker-compose up``` (Avec un fichier docker-compose.yaml), Faire la composition des conteurs décrit dans le ficher. 
- ```docker-compose down``` Arrêter tous les conteneurs du compose
- ```docker network ls``` Afficher la liste des network docker
- ```docker volume ls``` Afficher la liste des volumes docker

## 4. Exercices récapitulatifs

### 4.1. Mise en application simple

 Votre infrastructure est-elle conforme à ce qui était attendu?  Comment avez-vous pu la valider?  Donnez les commandes utilisées et illustrez le résultat par des screenshots. 

 L'infrastructure est bien conforme à ce qui était attendu, afin de pouvoir vérifier ceci, il a fallu : 
 - Vérifier que les 3 containers sont bien crées : 
![Création des containers](./pictures/4.1%20compose.png)
![Vérification des containers](./pictures/4.1%20containers.png)
 - Vérifier que les 2 réseaux sont bien crées : 
![Vérification des réseaux](./pictures/4.1%20networks.png)
 - Vérifier que les 2 volumes sont bien crées : 
![Vérification des volumes](./pictures/4.1%20volume.png)
 - Tester le volume docker des containersA et B en créant un ficher dans le volume partagé du containerA et vérifier qu'il existe bien dans le containerB : 
![Test volume docker](./pictures/4.1%20test_volume.png)
 - Tester que les containers puissent communiquer entre eux, et qu'ils soient bien isolés (communication possible entre A et B, et C et B, mais pas possible pour A et C car réseau pas en commun) :
![Test ping docker](./pictures/4.1%20networks_test.png)
 - Tester que le bind mount fonctionne en vérifiant la présence du src, sur l'ordinateur hôte
![Test bind mount docker](./pictures/4.1%20test_bind_mount.png)
### 4.2. Exemple du cours théorique

1. Dans cette infrastructure, comment les données sont-elles partagées?  Via des Bind Mounts ou des Volumes?  Pourquoi ? 

Le container Web utilise un Bind Mount : On y observer un lien entre le dossier de l'ordinateur hôte `/src` et le dossier `/app` à l'intérieur du container. Il est ici utilisé car cela permet à l'utilisateur de pouvoir modifier les fichiers sur son PC et de pouvoir voir les changements instantanément dans le container sans avoir à construire une image. 

Le container DB utilise un Volume : Le dossier `/mysql` du container est lié à un objet nomme `db-vol` qui rest représenté par un cylindre à l'intérieur de l'espace Docker. Il est ici utilisé car c'est la méthode recommandée pour les bases, cela permet d'avoir des meilleurs performances d'écriture et garantit que les données survivent même si le container et supprimé ou recréé. 

2. Quels sont les spécificités de chaque container? 

Le container Web est un serveur d'application web connecté au réseau interne `net`. Il est connecté sur le port interne 80 qui est relié au port 300 de la carte réseau de l'hôte (`eth0`), l'utilisateur peut donc y accéder via `http://localhost:3000`.

Le container DB est un serveur de base de donnés, qui est connecté au réseau interne `net`. Contrairement au container WEB, il n'y a pas de ports publié sur l'hôte il est ici isolé et donc seul le container WEB peut lui parler via le réseau docker. Enfin ce container utilise un volume nomme afin d'assurer une persistance des données fiable et sécurisée. 

3. Une fois démarrée, l'infrastructure est-elle conforme à ce qui était attendu?  Comment avez-vous pu la valider?  Donnez les commandes utilisées et illustrez le résultat par des screenshots. 

Oui l'infrastructure est conforme a ce qui était attendu, pour le valider : 

- Vérification de bon attributions des ports, on vérifie que le port 3000 de l'hôte est bien relié au port 80 du container :
![Vérification ports](./pictures/4.2%20services.png)
- Vérification du bind mount, on vérifie que le ficher hôte existe bien dans le container (dossier `/app` dans le container) :
![Vérification bind mount](./pictures/4.2%20bind-mount.png)
- Vérification du volume docker, on vérifie que le volume du container db existe bien et qu'il bien attaché à la DB : 
![Vérification volume docker](./pictures/4.2%20volume.png)
- Vérification du réseau, on fait un ping du container web vers le container db : 
![Vérification réseau](./pictures/4.2%20ping.png)

### 4.3. Exemple du tutoriel Docker

1. Quelles sont vos observations suite à la réalisation de ce tutoriel ?

Il est possible de mixer image personasliés, et les services, on peut utiliser des fichers de config pour python, séparer les services en plusieurs fichers. 

2. Sur quelle base les containers sont-ils lancés ? 

Elle tourne sur la base d'une image python avec un dockerfile, on y charge le programme python ainsi que les ports, on installe le compilateur et les bilothèques. 
Ensuite l'ensemble des services sont définis avec un dockercompose. On y connecte le port 8000 au port 5000 et il fait tourner le serveur depuis l'image de redis. 

3. Qu'avez-vous appris de nouveau ? 

Il est possible de découper les services d'un ficher compose, en plusieurs ficher yaml séparés, et les relies dans le ficher principal `compose.yaml`, il faut pour cela ajouter la ligne `include`, avec le nom des ficher a relier. 

Il est possible de faire des modifications en temps réel, avec l'aide du watch, cela permet d'éviter de monter un bind mount depuis le pc hôte.