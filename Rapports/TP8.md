# TP8 : Haute disponibilité et optimisation des performances 

Noms des auteurs :  DAUB Justin, EBERHART Yonas, GROLAUX Baptiste
Date de réalisation : 30/03/2026

# 1. Découverte Docker Swarm
## 1.2 Environnement de travail et organisation 

Pour la réalisation de cette partie, nous avons suivis, l'architecture qui été demandé, avec la recommendation d'avoir 3 `managers`. Pour ce faire nous avons donc renommée chacun de notre côté notre VPS, pour l'organiser de cette façon : 

- VPS de Justin : `manager 1`
- VPS de Baptiste : `manager 2`
- VPS de Yonas : `manger 3`

Le nom du VPS ce change avec la commande suivante : 
`sudo hostnamectl set-hostname manager1`

## 1.3 Mise en place de votre swarm 
### 1.3.1 Initialisation

L'initialisation d'un swarm docker s'effectue comme ceci : 
`docker swarm init`

*Note : Si le VPS a plusieurs adresses IP, Docker peut demande d'ajouter `-- advertise-addr <IP_publique> à la commande`.*

Une fois la commande tapé, la console affiche une ligne (`docker swarm join --token...`) avec un token qui serviront aux autres VPS de rejoindre ce cluster, **on copie donc cette ligne**.

Ensuite sur les autres VPS, on utilise ce token, pour que les autres puisse rejoindre ce cluster, pour s'assurer qu'il ont bien rejoin on regarde la liste avec `docker node ls` et on doit retrouver le noms des hôtes qui ont rejoint. 

### 1.3.2 Gestion des Node

Tapez `docker node` et observer les opérations disponibles dans cette catégorie de commandes.

- Comment changer le type d’un node?

Il faut utiliser les commandes de promotion et de rétrogradation depuis un manager : 
    - `docker node promote <nom_du_node>` : Permet de transformer un Worker en Manager.
    - `docker node demote <nom_du_node>` : Permet de transformer un Manager en Worker. 

- Quelles commandes `docker node `sont disponibles, et lesquelles pourraient vous être utiles ?

On peut voir des commandes utiles avec l'aide `docker node --help`, parmi-elles les plus utiles sont : 
    - `docker node ls` : Voir l'état du cluster (qui est manager, qui est *Ready* ou *Down*)
    - `docker node inspect <node>` : Pour voir les détails techniques d'une machine
    - `docker node rm <node>` : Pour retirer proprement une machine du cluster
    - `docker node update --availability drain <node>` : Vider une machine de tous les containers, utilise pour exemple faire une maintenance sur une machine.

### 1.3.3 Docker service

Pour déployer l'image web sur le cluster il faut depuis l'un des VPS (seulement un seul), réalise ces opérations : 

- **Créer le fichier `index.html`** : `echo "<h1>Hello depuis mon cluster Swarm !</h1>"`
- **Créer le `Dockerfile` avec l'image nginx personnalisé** : 

``` Dockerfile
FROM nginx:1.25.4
COPY ./index.html /usr/share/nginx/html/
```

- **Se connecter à Docker Hub** : `docker login -u <nom_utilisateur>`
- **Builder l'image** : `docker build -t <nom_utilisateur>/mon-site-swarm:v1 .`
- **Pousser l'image en ligne** : `docker push <nom_utilisateur>/mon-site-swarm:v1`

Puis enfin on lance le service : 
`docker service create --name web -p 8080:80 --replicas 2 <nom_utilisateur>/mon-site-swarm:v1`

Pour s'assurer du bon fonctionnement : 
- **On vérifie où tournent les conteneurs** : Avec la commande `docker service ps web`, on doit y observer que Swarm, les a répartis sur les différents VPS
- **Test de plantage** : On arrête un conteneur web sur l'un des VPS avec `sudo systemctl stop docker`, puis sur le vps manager on tape `docker service ps web`, on doit y observe que Swarm recréer automatiquement le conteneur perdu sur une machine qui marche. 

**Sur quel VPS le port est-il publié ?**

Il est publié : **Sur tous les VPS du cluster**.
Docker utilise un mécanisme appelé le **Routing Mesh**. 

Ex : Même si les 2 conteneurs tournent uniquement sur les VPS 1 et 2, même si on tape l'IP du VPS 3 dans le navigateur, et bien le VPS 3 va intercepter la requête et la rediriger en interne vers le VPS 1 ou 2

**Sur quels nodes va être exécuté ce service ?**

C'est le Manager qui décide, c'est lui qui généralement réparti les tâches de manière équitable sur les noeuds disponibles, on peut voir où ils se trouvent avec la commande : `docker service ps web`.

**Que se passe-t-il si vous stoppez un node (via `sudo systemctl stop docker`) ?**

Le Manager va détecter que le noeud ne répond plus, et apercevoir qu'il manque des replicas par rapport à la demande. Il recrée automatiquement les contenus perdus sur les noeuds qui fonctionnent encore.

**Que se passe-t-il si vous "scalez" votre service à un seul replica et que vous stoppez le node sur lequel il tourne**

Le service va subir une coutre interruption, le temps que le manager réalise que le noeud est mort, le site sera inaccessible. Ensuite, le Manager va recréer l'unique contenu sur au autre noeud vivant, et le service reviendra en ligne.

# 2. Un nouveau service Web pour WoodyToys
## 2.1 Découverte de l'application

- Parcourez les fichiers de ce repository : Quelle technologie se cache derrière chaque service?

  - **Le Serveur Web/Reverse Proxy (L'entrée)** : **Nginx**, il se charge d'accueillir les requêtes des utilisateurs, de servir les fichiers simples, et de rediriger les requêtes complexes vers l'API.
  - **Le Frontend (l'interface visuelle)** : Ce sont les fichiers statiques **HTML, CSS et des images** (*représentés par l'icône de code et d'image sur le schéma*)
  - **Le Backend/L'API (la logique métier)** : **Flask** (un framework écrit en Python représenté par l'icône de la corne). Il a pour rôle de traiter des requêtes comme les commandes ou les calculs lourds.
  - **La base de données (le stockage)** : **MySQL** (représenté par le dauphin). Son rôle est de stocker les données persistantes comme la liste des produits ou l'historique des commandes.

- Quels sont les flux de données dans cette application ? Identifiez-le sur le schéma, et indiquez chaque fois le protocole utilisé. Documentez soigneusement ces flux sur votre Wiki.

A travers ce schéma on identifie 3 flx de données : 

1. **Utilisateur <-> Nginx** :
   - **Flux** : Le navigateur de l'utilisateur demande à afficher la page web ou envoie une action
   - **Protocole** : **HTTP** (Port TCP 80) ou **HTTPS** (Port TCP 443).

2. **Nginx <-> Fichiers Statiques (HTML/Images)** :
   - **Flux** : Nginx va chercher les pages HTML et l'image de 5 Mo pour les renvoyer directement à l'utilisateur.
   - **Protocole** : Lecture de fichiers locaux (I/O système) ou HTTP interne si le font est dans un conteneur séparé.

3. **Nginx <-> Flask (Backend)** :
   - **Flux** : Quand l'utilisateur demande une action dynamique (ex : `/api/products`), Nginx fait office de *Reverse Proxy* et transfère la requête à l'API Flask.
   - **Protocole** : **HTTP** ou parfois uWSGI.

4. **FLask <-> MySQL** :
   - **Flux** : L'API interroge la base de données pour lire le dernier produit ajouté ou enregistrer une nouvelle commande
   - **Protocole** : Protocole propriétaire **MySQL** (sur le port TCP interne 3306)

- Clonez le repository applicatif sur un de vos VPS, et lancez le fichier Docker-Compose (`docker compose up --build`). Arrivez-vous à accéder à la page web ? Si ce n’est pas le cas, vérifiez votre firewall et adaptez éventuellement vos règles ou les numéros de port utilisés par cette application

En ayant libéré tous les ports nécessaire dans notre par-feu, nous avons pu accéder au site-web depuis l'adresse de notre domaine. 

## 2.2 Déploiement de l'application sur Docker Swarm

Pour déployer l'application, il faut publier toutes les images docker personnalisé de l'application. Un script ayant été mis à notre disposition nous l'avons utilisé pour générer les images personnalisé : 

`sed -i 's/xdubruille/<votre-username-docker-hub>/g' build_push.sh`

On le rend exécutable :

`chmod +x build_push.sh`

Et on exécute le script : 

`./build_push.sh`

Il ne reste maintenant plus qu'à personnaliser le docker-compose, avec nos images personnalisé : 

``` YAML
version: "3.9"

services:
  db:
    image: <username>/woody-db:latest
    cap_add:
      - SYS_NICE
    environment:
      - MYSQL_DATABASE=woody
      - MYSQL_ROOT_PASSWORD=pass

  api:
    image: <username>/woody-api:latest
    deploy:
      replicas: 2

  front:
    image: <username>/woody-front:latest
    deploy:
      replicas: 2 

  reverse:
    image: <username>/woody-reverse:latest 
    ports:
      - "80:8080"
    depends_on:
      - front
      - api
```

On déploit : 
`docker stack deploy -c docker-compose.yml woodytoys`

Puis on vérifie :
- `docker stack ls` (Pour vérifier que la stack est actif)
- `docker stack ps woodytoys` (Pour voir sur quel VPS tourne chaque conteneur)

# 3. Analyse de la robustesse

Afin de mettre en place le round-robin nous avons pris le fichier de zone du vps de justin, et nous avons placé les IPs de nos VPS respectifs : 

``` Plaintext
www     IN      A       91.134.138.155   ; (VPS manager1)
www     IN      A       51.210.33.44     ; (VPS manager2)
www     IN      A       141.94.77.88     ; (VPS manager3)
```

On fait ensuite en sorte que le revese proxy tourne sur tout le machine on paramétrant la section `reverse` du docker compose et en mettant le deploy en mode `global`: 

``` YAML 
reverse:
    image: <ton-username>/woody_rp:latest
    ports:
      - target: 8080
        published: 80
        protocol: tcp
        mode: host
    deploy:
      mode: global # <-- Remplace 'replicas: 1'. Swarm mettra exactement 1 conteneur sur CHAQUE node du cluster.
    depends_on:
      - front
      - api
```

Et on redéploie les services pour que les modifications soient prises en compte : 
`docker stack deploy -c docker-compose.yml woodytoys`


# 4. Analyse et ajustement des performances

## 4.1 Campagne de mesure

### 1. Evaluation du chargement initial de la page

Pour réaliser ce test on a : 

1. Ouvert le navigateur sur `http://www.l1-10.ephec-ti.be`
2. Ouvert les **DevTools** (touche `F12`)
3. Sélectionner l'onglet **Réseau** (ou *Network*)
4. Cocher la case **"Désactiver le cache"** (ou *Disable cache*) pour forcer le téléchargement complet.
5. Rafraîchis la page (`F5`)
6. Noter le temps (*voir photo ci-dessous*)

![Résultat du chargement initial](../TP8/pictures/4.1%20Test%20chargement%20initial.png) 

Lors de cette mesure, on constate que le chargement global de la page échoue (*Timeout*) à cause du fichier statique `5mo.jpg`. Le serveur Front-End est trop lent (throtlé) pour distribuer ce fichier volumineux, ce qui provoque une erreur `504` *Gateway Timeout* au niveau du Reverse Proxy après 60 secondes.

### 2. Mesure des requêtes isolées

![Résultat requêtes isolés](../TP8/pictures/4.1%20Test%20requêtes%20isolés.png)

Après exécution du script qui teste la route `/api/misc/heavy`, on observe un temps de réponse trop élevé qui se termine à 60 secondes. Cela est dû à l'opération qui est lourde, en plus du bridage du serveur Flask (*qui est limité à 1 seule connexion simultanée*).

### 3. Mesure de la résistance à la charge

![Résultat mesure de résistance à la charge](../TP8/pictures/4.1%20Test%20résistance%20à%20la%20charge.png)

Lors du test de résistance à la charge (*quêtes simultanés*) sur la route `/api/misc/time`, on observe que toutes les requêtes ont renvoyé un temps de réponse d'environ 60 secondes. Cela implique que le serveur Flask (*bridé à une connexion*) n'a pas pu traiter la charge. Les requêtes en attente ont toutes été coupées par le *Timeout* (60s) du Reverse Proxy.

## 4.2 Augmentation du nombre de containers

Afin d'augmenter le nombre de containers, il ne faut ajuster le nombre de contenus en direct pour chacun des services : 

- **API** : Très important de l'augmenter car un conteneur Flaks ne peut gérer qu'une requête à la fois, on a met 10, afin que les 10 requêtes puissent être traiter en parallèle
- **Front-End** : On l'augmente aussi, car il a du mal à faire passer l'image de 5 Mo, on répartis la charge sur plusieurs Front, on en met 5
- **Reverse Proxy** : Pas besoin d'y toucher car on l'a déjà mis en `mode: global` (*1 par machine*). 
- **Base de données** : **Il ne faut surtout pas l'augmenter**, Si on lance 3 conteneurs de DB en même temps, alors les autres conteneurs vont s'emeller entre eux pour écrire sur les mêmes fichiers et corrompre les fichier, on le laisse donc à 1. 

On augmente tout ceci de cette façon :

`docker service scale woodytoys_api=10 woodytoys_front=5`

Et obtient ce résultat : 

![Résultat après augmentation de services](../TP8/pictures/4.2%20Test%20après%20augmentation%20service.png)

Est-ce que l’augmentation du nombre de replicas résout certains problèmes ? Répondez en comparant les premiers chiffres de performance observés avec des mesures effectuées après la modification. Pour chacune des limitations, commentez les éventuelles améliorations en étant critiques (les limitations artificielles ne sont peut-être pas représentatives de la réalité).

Suite au passage à 10 replicas pour l'API, le test de charge a montré une nette amélioration : 3 requêtes ont répondu instantanément (0.01s), cela montre que la parallélisation fonctionne et que le goulot d'étranglement de Flask est contourné. Les 7 autres requêtes ont fait un *Timeout*, ce qui met en évidence un blocage du trafic interne (*réseau Overlay*), par le pare-feu des autres noeuds du cluster. La théorie de l'augmentation des replicas est donc validée, sous réserve de configurer les règles *UFW inter-noeuds*. 

Est-ce qu’il y des choses que vous pouvez mettre en place au niveau de Docker Swarm (outre les réplicas) pour améliorer les performances ? (Hints: healthchecks(pour l’api) et placement constraint (pour la base de données))

Oui il y a des choses que nous pouvons mettre en place au niveau de Docker Swarm pour améliorer les performances, comme par exemple : 
    - **Les Healthchecks (pour l'API et le Front)** : A l'état actuel, si le serveur Flask "freeze" complètement pendant un gros calcul et arrête de répondre, Swarm ne le sais pas (car le conteneur lui-même n'a pas crashé, il tourne toujours dans le vide). En ajoutant une instruction `healthcheck` (un test de santé régulier, comme un `curl localhost/ping`), Swarm saura détecter qu'un conteneur est devenu "zombie" et le redémarrera automatiquement. 
    - **Les Placement Constraints (pour la base de donnée)** : Actuellement si le conteneur `db` plante, Swarm peut le relancer sur le `manager2` ou `manager3`. Mais le problème c'est que les données sauvegardées (les vrais fichiers de la base) sont restées sur le disque dur du `manager1`, la base redémarre donc vide ! Pour y remédier il faut utiliser un `placement constraint` (ex: `node.role == manager` ou `node.hostname == manager1`), cela permet de forcer Swarm à toujours faire tourner la base de données sur la machine physique où se trouvent ses données.

## 4.3 Mise en place d'un cache 

On détermine d'abord les fonctionnalités que l'on peut améliorer avec le cache : 
    - `/api/misc/heavy` : **Amélioration possible**, c'est un calcul lourd basé sur un paramètre. Si on demande 10 fois le même paramètre, le résultat sera le même, il convient donc le mémoriser.
    - `/api/products/last` : **Amélioration possible**, la requête SQL est lente, tant que personne n'ajoute de nouveau produit, le "dernier produit" reste le même, c'est donc cohérent de mettre un cache.
    - `/api/misc/time` : **Pas d'amélioration possible**, l'heure n'arrête pas de changer, si on le mettait en cache pour 60 secondes, l'API renverrait une heure fausse pendant une minute
    - `Ajouts/commandes (POST)` : **Pas d'amélioration possible**, on ne cache jamais une action d'écriture ou de paiement

On ajoute ensuite Redis, dans le fichier `docker-compose.yml`, en ajoutant un nouveau service `redis` : 

``` YAML
redis:
    image: redis:alpine
    deploy:
      replicas: 1
```

Ensuite il faut modifier le code principal (le fichier `main.py`), pour importer la bibliothèque de `redis`, et l'utiliser pour les routes nécessaires. L'ajout en question ressemble à celui-ci : 

``` Python
import redis
# ... autres imports ...

# Connexion à Redis (le hostname est le nom du service dans le docker-compose)
redis_db = redis.Redis(host='redis', port=6379, db=0)

@app.route('/api/misc/heavy', methods=['GET'])
def get_heavy():
    name = request.args.get('name')
    
    # 1. On vérifie si la réponse est déjà dans le cache
    cached_response = redis_db.get(name)
    
    if cached_response is None:
        # 2. Si RIEN n'est en cache, on fait le calcul (qui prend 60 secondes)
        response = simulate_heavy_computation(name) 
        
        # 3. On sauvegarde le résultat dans Redis pour 60 secondes !
        redis_db.setex(name, 60, response)
        return response
    else:
        # 4. Si c'est en cache, on renvoie directement (ça prend 0.01 seconde !)
        return cached_response
```

**Et on oubli pas de reconstruire l'image après la modification !**

Maintenant que le cache est mise en place, on relance un nouveau test, pour voir observer les effets de la mise en place du cache : 

![Résultat après la mise en place du cache](../TP8/pictures/4.3%20Test%20après%20cache.png)

Est-ce que cette cache améliore les performances ? De combien ? Pour toutes les requêtes?

Oui et de manière très sgnificatif, le temps de réponse est passé de 60 secondes à seulement quelques millisecondes (*ce qui fait une amélioration de plus de 99% !*). Néanmoins ce n'est pas le cas pour toutes les requêtes, par exemple pour la toute première requête (*le "cache miss"*), il y a toujours la lenteur initiale. De plus le cache n'est pas applicable aux requêtes d'écriture, ou aux données en temps réel (l'heure).

## 4.4 Utilisation d'un cache CDN (Bonus)

Afin de pouvoir ajouter un cache CDN, on se rend sur *Gcore*, on l'on se crée un compte,

Ensuite on clique sur `Get started for free`, et on remplis les cases avec ces infos : 
  - **Add domain** : `cdn.l1-10.ephec-ti.be`
  - **Origin source** : `www.l1-10.ephec-ti.be`

Une fois l'adresse généré par le site, on l'ajoute dans le fichier de zone, avec cette nouvelle ligne :

`cdn     IN      CNAME   cl-xxxxxx.gcdn.co.`

Ensuite on ouvre le fichier HTML du site, afin de forcer le navigateur à utiliser les images du cache CDN :

```HTML 
<img style="position: absolute ; top:0 ; left: 0; z-index: -100;" src="http://cdn.l1-10.ephec-ti.be/5mo.jpg" alt="image"/>
```

**Et on rebuild limage du front pour la mise à jour du code**

Malgré que nous ayons réussi à mettre en place le CDN (*vérifiée par le chargement du HTML via l'URL du CDN*). Nous nous sommes aperçu d'une importante limite : **un CDN ne peut pas mettre en cache un fichier s'il est incapable de le télécharger une première fois depuis l’origine**. Le serveur Front-End est trop bridé que cela provoque une coupure de connexion (`ERR_CONNECTION-RESET`) lorsque le CDN tente de récupérer l'image de 5 Mo.

**Conclusion** : Le CDN se révèle être une excellente solution pour la mis eà l'échelle globale, mais le ne remplace pas la nécessité d'avoir un serveur origine suffisamment robuste pour servir au moins un "Cache Miss" complet. 

## 4.5 Base de données (Bonus)

Pouvez-vous citer et expliquer une solution pour améliorer les performances au niveau d’une DB? (une brève description et la présentation de l’un ou l’autre avantage, inconvenient, particularité, … sont suffisants). L’image ci-dessous vous illustre une solution possible.

Une solution qui permettrait d'améliorer les performances au niveau d'une DB sont **les réplicas de lecture (read replicas)**. Son principe consiste à séparer les tâches. Il garde un serveur **"Master"** (Primaire), et il a plusieurs autres serveurs **"slaves"** (Secondaires/Réplicas).

### 1. Comment ça marche ? 
- **Le Master (Ecritures)** : Toutes les opérations qui modifient les donnés (`INSERT`, `UPDATE`, `DELETE`) vont sur ce serveur.
- **Les Réplicas (Lectures)** : Le Master recopie en temps réel ses données vers les réplicas. Toutes les requêtes de consultations (`SELECT`) sont envoyées vers ces réplicas.

### 2. Avantages et inconvénients

| Caractéristique          | Détails                                                                                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Avantage principal**   | **Décharge le Master :** Dans 90 % des apps web (comme WoodyToys), il y a beaucoup plus de gens qui regardent les produits (lectures) que de gens qui en achètent (écriture).        |
| **Haute disponibilité**  | Si un réplica tombe, les autres continuent de répondre. Si le master tombe, on peut "promouvoir" un réplica pour qu'il devienne le nouveau Master.                                   |
| **Inconvénient (Délai)** | **Réplication Lag :** Il peut y avoir quelques millisecondes de retard. Un utilisateur pourrait ajouter un produit et ne pas le voir tout de suite s'il rafraîchit la page trop vite |
| **Complexité Code**      | L'application (le code Python) doit être capable de gérer 2 connexions : une pour lire et une pour écrire                                                                            |