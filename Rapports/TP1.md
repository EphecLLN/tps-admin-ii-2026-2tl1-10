
Noms des auteurs : DAUB Justin, EBERHART Yonas, GROLAUX Baptiste

Date de réalisation : 02/02/2026

## 1. Premier container

### 1.1. Hello World 

Pouvez-vous expliquer avec vos mots ce qui s'est passé suite à l'exécution de cette commande? 

Après l'exécution de cette commande, docker n'arrive pas à trouver l'image 'hello-world:lastest' localement, ce qui signifie que l'image n'est pas présente sur la machine. 

Étant donnée que l'image n'existe pas il va aller chercher la libraire en ligne afin de récupérer l'image, ensuite une fois l'image trouvé il télécharge l'image de hello world. 

Une fois cela fait il affiche le message "Hello from Docker!", signifiant que l'image a été téléchargé et fonctionne correctement. 

Dans la console l’ensemble des résultats est le suivant : 

![Hello world avec l'image hello_world](/TP1/pictures/1.1%20hello_world.png)

### 1.2.  Observer un container


Retrouvez les informations suivantes sur le container lancé précédemment : 
1. Quel est son identifiant ? 

L'identifiant est : `aaf130ade8ac`

2. Quel est son nom ? 

Le nom du conteneur est : `objective_leakey`

3. Quel est son état ? 

Le status est : `Exited (0) 5 minute ago`, Autrement-dis l'image a été arrêté, car il a finis son exécution

4. Quel est le nom de son image?  Avez-vous vu au point 1.1. d''où cette image provenait?

Le nom de l'image est : `hello-world`. D'après le résultat obtenus dans le point 1.1, on constate que l'image provient de : `library/hello-world`

5. Quelle commande le container a-t-il exécuté? 

La commande exécutée par le container est : `/hello`

6. Si vous avez installer Docker Desktop, pouvez-vous retrouver ces mêmes informations dans l'interface graphique? 

Oui, depuis l'application nous pouvons observer dans l'interface des containers avec les mêmes informations observés depuis le terminal. 

![Interface de docker desktop](/TP1/pictures/1.2%20docker_desktop.png)

### 1.3. Les images 

1. Quelles informations voyez-vous?  Quel est le lien avec ce que vous avez observé auparavant? 

Cette fois ci nous avons le nom de l'image, ainsi que son ID associée. Contrairement au container on peut voir la taille de l'image ainsi que la quantité de mémoire utilisée sur le disque. Enfin il affiche une info nommée "Extra", indiquant qu'il est utilisée avec la lettre "U". 

2. Comparez l'output de cette commande avec la vue correspondante de l'interface graphique.  

En allant dans l'interface graphique de cette image (accessible en cliquant dans le nom de l'image de notre conteneur), on peut contrairement au terminal voir ce qui a été exécutée ainsi que la taille que cela prend. Ensuite tout comme le terminal on retrouve bien l'ID, ainsi que la taille. Enfin une autre info pouvant être uniquement observé sur l'interface graphique depuis combien de temps l'image est créer.  

3. Essayez de trouver la commande qui vous permettra de supprimer cette image.  C'est une bonne idée de ne pas conserver les images non utilisées sur votre système de fichiers : même avec la mutualisation de couches, elles prennent de l'espace sur le disque! 

Pour pouvoir supprimer une image sur le disque il faut utiliser la commande `docker rmi <id_image ou nom_de_l_image>`. En reprenant l'ID de notre image, on constate que par défaut la supression ne fonctionne pas. 

La raison est que la suppression doit être forcée, car elle est utilisée dans un container (celui que nous avons crées), il faut pour cela ajouter l'option -f qui force la suppression. Et en ajoutant cette option, l'image est bien supprimée 

## 2. Utiliser un container

### 2.1. Interagir avec un container

1. A quoi servent les options ```i``` et ```t```dans la commande ci-dessus? 

- L'option `i` permet de préciser au conteneur de recevoir ce qui est tapé au clavier sans ceci le conteneur ne pourrait pas prendre en compte les commandes. 
- L'option `t` permet de faire en sorte que le texte s'affiche correctement et de faire en sorte qu'il soit comprehensible pour un humain. Elle permet d'afficher le terminal ainsi que les lignes. 
Nous combinions ainsi ces 2 options entre elles pour pouvoir écrire les commande et faire en sorte d'afficher le terminal. 

2. Chaque container Docker est destiné à exécuter une commande unique.  Quelle est-elle dans ce cas-ci? 

En faisant la commande `docker container ls -a` pour observer le container de ubuntu, la commande exécutée est `bash`, qui permet de lancer le terminal Linux.

3. Dans le container, quels sont les processus présents?  Et leurs PIDs? 

A l'intérieur du container on exécute la commande `ps`, pour lister les processus. Il y en a 2 : 
- `bash` avec un PID de 1 
- `ps` avec un PID de 9
  
4. Avec quel utilisateur êtes-vous loggé? 

On est logée avec l’utilisateur root, d'après le nom affichée à gauche de chaque nouvelle ligne

5. Votre container a-t'il accès à Internet?  Qui est son résolveur? 

Pour vérifier que le container à accès à Internet, on essaye de mettre à jour les librairies avec `apt-get update`, puis on observe bien les lignes montrant qu'il télécharge les mises à jour ce qui prouve qu'il est connecté à internet.
Pour connaitre son résolveur, on regarde le fichier resolv.conf dans le dossier etc, avec `cat /etc/resolv.conf` en regardant le contenu du ficher on voit écrit 'nameserver 192.168.65.7'. Le résolveur est donc `192.168.65.7`. 

### 2.2. Inspecter un container

1. Chaque container dispose d'une interface réseau.  Quelle est l'adresse **IP** de l'interface de votre container? 

Avec `docker inspect`, en cherchant dans les informations on trouve une section 
"NetworkSettings" avec "IPAddress", et on trouve que l'adresse IP est `172.17.0.1`

2.  Votre container a-t'il des **ports** ouverts?  

Non en observant l'endroit où les ports sont indiqués, il y a une liste vide, ce qui signifie qu'il n'y a pas de ports ouverts. 

### 2.3. Faire tourner un service dans un container

Qu'avez-vous observé au niveau des "ports" ?  Expliquez et illustrez votre réponse avec des screenshots. 
  
En testant les 2 commandes, nous avons crées pour les 2 situations le port 80 sur lequel on veut mettre le serveur en écoute. Mais la différence majeure est que pour la 1ère commande le port 80 n'est pas reliée, et en inspectant le conteneur, on repère bien le port 80 mais il affiche une 
valeur nulle, cela est du au fait que nous n'avons pas connecté le port 80 à un port localhost. 

Pour la deuxième commande on a ajouté l'option `-p`, et si on inspecte le conteneur, on a cette fois bien des informations avec le port de l'hôte et l'ip de l'hôte, ce qui indique qu'il y a bien une connection avec l’ordinateur de l'hôte sur un localhost. Ensuite si dans le navigateur de l'hôte on va sur le local host du port 80, on retrouve bien la page web du serveur, ce qui indique son bon fonctionnement.

## 3. Construire des images

### 3.1. Figer un container 
#### Partie 1 : Personnalisation du index.html du serveur 

On vérifie d'abord que le serveur fonctionne toujours avec `docker container ls` et on constate que l'état du container avec le serveur est bien sur up signifiant qu'il est actif. 
Ensuite dans ce container on exécute le bash avec `docker exec -it mon-serveur-web bash`. 

A l'intérieur on met à jour les bibliothèques avec `apt-get update`, et ensuite on installe nano pour éditer le ficher HTML, ainsi que netstat pour vérifier que le port sont bien sur écoute avec `apt-get install -y nano net-tools`. 

On ouvre le ficher avec nano : `nano /usr/share/nginx/html/index.html`, on change le contenu, puis on sauvegarde avec `CTRL + 0` puis `Entrée`, puis on quitte l’éditeur avec `CTRL + X`. On sort ensuite avec `exit` du bash puis en allant dans le localhost on retrouve bien la page avec le html personnalisé. 

#### Partie 2 : Création d'une image personnel du serveur

Pour effectuer créer l'image on fait `docker container commit mon-serveur-web nginx`
On vérifie qu'il existe dans la liste des images avec `docker image ls`, on le trouve bien dans la liste 

On arrête l'ancien container avec `docker stop <id_container>`

On l'exécute ensuite : `docker run -it nginx`, puis en allant sur le localhost du port 80, on retrouve toujours bien la page html personnalisé.

### 3.2. Créer une image sur base d'un Dockerfile

Sur la machine hôte on créer un dossier avec un dockerfile, et le contenu suivant : 

``` dockerfile
FROM nginx:latest
RUN apt update
RUN apt install -y nano net-tools
COPY index.html /usr/share/nginx/html
```
On y ajoute un index.html, puis ensuite on construit l'image de la manière suivante : `docker build -t mon_serveur .`

Enfin on test on se connectant au port 80 du localhost, et on trouve bien depuis cette image la page personnalisé. 

## Exercices récapitulatifs

Documentez ici la réalisation des exercices, via des explications et des snapshots. 
### 4.1. Démarrer un serveur Web Apache

#### Partie 1 : Trouver l'image 
On a d'abord tapé sur internet, image apache server, cela m'a ensuite redirigé vers dockerhub, où on a trouvé que le nom de l'image recherché est `httpd`.

![Site DockerHub avec l'image](/TP1/pictures/4.1%20image%20apache.png) 

#### Partie 2 : Démarrer le container sur l'image de apache + 2 ème virtual host
On souhaite d'ici la suite de cette exercice avoir 2 virtual host avec des port différents il nous faut pour cela configurer les ports avec l'option `p`, que l'on met 2 fois pour configurer 2 virtualhosts :

`docker run -it -p80:80 -p8080:8080 httpd`

L'image est ensuite téléchargé et nous avons créer le conteneur avec l'image de apache. 

En allant sur le localhost on a bien la page : 
![Localhost par défaut avec apache](/TP1/pictures/4.1%20localhost.png)

#### Partie 3 : Création des pages d’accueils personnalisées  
Avec apache le ficher de la page d’accueil `index.html` se trouve dans `/usr/local/apache2/htdocs`, On crée 2 dossier avec un pour chaque site pour y stocker la page d’accueil pour chaque site respectif. 

Ensuite, il nous faut configurer les 2 virtualhosts, notamment pour lier chacunes de ces 2 pages d'accueils au bon port. Il faut modifier avec nano le ficher de config situé à `/usr/local/apache2/conf/httpd.conf`. On modifie ce ficher et on met le contenu suivant à la fin du fichier : 
``` apache
# On indique à apache d'écouter sur le port 8080 (déjà fait pour le port 80 plus haut de le fichier)
Listen 8080 
# Configuration Site 1 (Port 80)
<VirtualHost *:80>
    DocumentRoot "/usr/local/apache2/htdocs/site1"
    <Directory "/usr/local/apache2/htdocs/site1">
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>

# Configuration Site 2 (Port 8080)
<VirtualHost *:8080>
    DocumentRoot "/usr/local/apache2/htdocs/site2"
    <Directory "/usr/local/apache2/htdocs/site2">
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```
Une fois cela fait on va sur le localhost des 2 ports, et on retrouve bien la page personnalisé avec les 2 ports : 

Port 80 : 
![Localhost port 80](/TP1/pictures/4.1%20localhost%20perso%20port80.png)

Port 8080 :
![Localhost port 8080](/TP1/pictures/4.1%20localhost%20perso%20port8080.png) 

#### Partie 4 : Réalisation de l'image personnalisée avec le DockerFile
On prépare un dossier nommée `apache-auto`, dedans on met un dossier site1 et site2 avec leur index.html respectif pour chacune des pages des 2 ports. A la racine on met le dockerfile ainsi que le ficher de config. 

On personnalise d'abord le contenu des 2 fichiers HTML puis on configure le ficher de config nomme `vhosts.conf`. On y remet le même contenu comme fait dans le ficher de config précédemment. 

Une fois l'ensemble préparer on s'occupe du Dockerfile, on récupère d'abord l'image d'appache, on copie les 2 dossiers des sites à l'intérieur du conteneur, on y copie le ficher personnalisé, et on ajoute dans le ficher de config du conteneur 2 lignes pour ouvrir le port 8080 et mettre le ficher de configuration personnalisé. Le Dockerfile est de cette forme : 

``` dockerfile
# 1. Image de base
FROM httpd:latest

# 2. Copie des sites web
# On copie le contenu local vers le dossier du serveur dans le conteneur
COPY ./site1/ /usr/local/apache2/htdocs/site1/
COPY ./site2/ /usr/local/apache2/htdocs/site2/

# 3. Copie de notre ficher de config personnaslié 
COPY ./vhosts.conf /usr/local/apache2/conf/vhosts.conf

# 4. Modification du ficher de configuration principal (httpd.conf)
# On ajoute deux lignes à la fin du fichier principal : 
# - Listen 8080 : Pour ouvrir le port
# - Include ... : Pour charger notre fichier vhosts.conf créé plus haut 
RUN echo "Listen 8080" >> /usr/local/apache2/conf/httpd.conf && echo "Include /usr/local/apache2/conf/vhosts.conf" >> /usr/local/apache2/conf/httpd.conf
```

On contruit l'image avec l'ensemble de ces configurations :

`docker build -t apache-auto .`

Puis on l'exécute : 

`docker run -p 80:80 -p 8080:8080 apache-auto`

Et à ce moment on se reconnectant sur les 2 localhosts on retrouve bien les pages personnalisées comme effectué auparavant. 

### 4.2. Lancer un résolveur Bind dans un container Docker

1. Quelle configuration avez-vous effectuée au niveau des ports ? 

En allant sur le dockerHub il existe effectivement une image avec bind installée. Il s'agit de l'image : `ubuntu/bind9`

Une fois installé on démarre notre image ubuntu avec bind sur le port 53 avec l'aide de la commande : `docker run -d --name mon-bind -p 53:53/udp -p 53:53/tcp ubuntu/bind9`

Une fois cela fait on vérifie que le serveur répond correctement avec l'aide de `nslookup` (sur windows) sur le localhost, vers par exemple google.com. On obtient ensuite une réponse avec une adresse IP ce qui montre que le serveur fonctionne.

Ensuite il faut configurer le fowarder que nous avons fait aller vers 8.8.8.8. Pour ce faire on : 

- Entre dans le conteneur : 

`docker exec -it mon-bind bash`

- Installe nano (car il est pas installé avec l'image par défaut)

`apt-get update && apt-get install -y nano`

- Edite le ficher de configuration 

`nano /etc/bind/named.conf.options`

- Modifie le fichier pour s'assurer que le allow-query est sur any : 

``` bash
options {
    directory "/var/cache/bind";

    # 1. Autoriser tout le monde (essentiel en Docker)
    allow-query { any; };
    recursion yes;

    # 2. Le Forwarder vers Google
    forwarders {
        8.8.8.8;
    };

    dnssec-validation auto;
    listen-on-v6 { any; };
};
```

- Effectue un redémarrage du service pour que les modifications soient prises en compte

`service bind9 restart`

2. Qu'avez-vous observé dans la trace Wireshark qui prouve que la configuration est correcte?  Illustrez avec un screenshot de la capture.

On observe que : 

- Sans Fowarder : Le conteneur interroge les "Root Servers" (des IPs variées partout dans le monde).
- Avec Fowarder : Le conteur envoie la requête directement à 8.8.8.8 (Google)

On repère sur la capture wireshark : 

- Source : IP locale
- Destination : 8.8.8.8
- Protocol : DNS
- Info : Standard Query "apple.com"

![Caputre wireshark de la configuration](/TP1/pictures/4.2%20Wireshark.png)

### 4.3. Container avec script Python
Pour afficher la date avec python, on crée un dossier contenant le script python affichant la date avec son dockerfile.

Dans le dockerfile, on récupère directement l'image de python, on définit ensuite dans le conteneur un dossier de travail dans lequel va s'exécuter le script avec la commande `WORKDIR` :

``` dockerfile
# 1. On part d'une image Pyton légère (slim)
FROM python:3.9-slim

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. Copie du script du PC hôte vers le conteneur
COPY date.py . 

# 4. La commande qui se lance au démarrage
# A la fin de cette commande, le contenur s'éteint
CMD ["python", "date.py"]
```

On copie ensuite le script python de la machine hôte vers le conteur, puis avec la commande `CMD`, on ordonne à notre conteneur d'exécuter le ficher `date.py` avec python. L'utilisation de cette commande permets aussi d'éteindre le conteneur dès que le script a été exécutée. 

A l'exécution on retrouve bien la date d'aujourd'hui avec l'heure d'exécution : 
![Script avec date et heure d'aujourd'hui](/TP1/pictures/4.3%20date.png)