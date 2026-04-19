# TP9 : Microservices et Message Broker 

Noms des auteurs :  DAUB Justin, EBERHART Yonas, GROLAUX Baptiste
Date de réalisation : 13/04/2026

# 1. Microservices
## Mise en place
Afin de pouvoir diviser l'application en plusieurs microservices, on modifie le fichier docker-compose.yml, et on ajoute des nouveaux blocs de services pour chacun des apis :

- `api-products`
- `api-user`
- `api-misc`

*Note : Pour chacun des services nous mis dans le bloc `deploy`, un sous-bloc `placement` avec à l'intérieur le bloc `constraints`, qui contient cette ligne `node.hotsname == manager1`. Cela permet de forcer l'exécution sur la machine du manager1 (celle de justin), car l'un des 2 autre machines avait un problème, et empêchait l'exécution* 

Et à la fin du fichier afin que le bon fichier de configuration nginx soit lu, on met un bloc `configs` avec le chemin d'accès au fichier de configuration.

Concrètement le `docker-compose.yml`, ressemble maitenant à ceci : 

``` YAML
version: "3.9"

services:
  db:
    image: gloutamax/woody_database:latest
    networks:
      - woodynet
    deploy:
      placement:
        constraints:
          - node.hostname == manager1
    cap_add:
      - SYS_NICE
    restart: always
    environment:
      - MYSQL_DATABASE=woody
      - MYSQL_ROOT_PASSWORD=pass

  redis:
    image: redis:alpine
    networks:
      - woodynet
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.hostname == manager1

  api-products:
    image: gloutamax/woody_api:v4
    networks:
      - woodynet
    deploy:
      replicas: 5
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - db
      - redis

  api-users:
    image: gloutamax/woody_api:v4
    networks:
      - woodynet
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - db
      - redis

  api-misc:
    image: gloutamax/woody_api:v4
    networks:
      - woodynet
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - db
      - redis

  front:
    image: gloutamax/woody_front:v4
    networks:
      - woodynet
    deploy:
      replicas: 2

  reverse:
    image: gloutamax/woody_rp:latest
    networks:
      - woodynet
    volumes:
      - ./reverse-proxy/default.conf:/etc/nginx/conf.d/default.conf
    ports:
      - target: 80
        published: 80
        protocol: tcp
        mode: host
    deploy:
      mode: global
    depends_on:
      - front
      - api-products
      - api-users
      - api-misc

networks:
  woodynet:
    driver: overlay

configs:
  nginx_config:
    file: ./reverse-proxy/default.conf
```

Ensuite on modifie le fichier de configuration nginx, qui est ici appelé `default.conf`. Dedans il faut déclarer les routes utilisés, et les paramètres pour que les routes soient dirigés vers les bon conteurs.

``` Nginx
server {
    listen 80;
    server_name localhost;

    # --- MICROSERVICES API ---

    location /api/products {
        proxy_pass http://api-products:5000;
        proxy_set_header Host $host;
    }

    location /api/orders {
        proxy_pass http://api-users:5000;
        proxy_set_header Host $host;
    }

    location /api/misc {
        proxy_pass http://api-misc:5000;
        proxy_set_header Host $host;
    }

    # --- FRONT-END ---
  
    location / {
        proxy_pass http://front:80; 
        proxy_set_header Host $host;
    }
}

```

## Réflexion sur le scaling
*Réfléchissez à un “scaling” de chaque microservice indépendamment des autres. Quels endpoints pourraient être les plus sollicités ou les plus lents ?*

Les endpoints qui pourraient être les plus sollicités sont les suivants : 

- **Les lectures (GET /api/products)** : Sur un site e-commerce, on lit beaucoup plus de produits qu'on n'en achète. Il faudra donc peut être le "scaler" (ex : 3 instances).
- **Heavy Computation (/api/misc)** : Si on a une route qui génère des PDF de factures ou qui fait des calculs lourds, elle risque de bloquer le CPU du conteneur. Il faut de ce cas la séparer et potentiellement la scaler pour qu'elle ne ralentisse pas l'affichage des produits.

Il sera possible de réaliser cette opération pour un service spécifique avec Docker Compose, on pourra utiliser la commande : `docker-compose up -d --scale api-misc=3`

## Test des microservices
### Etape 1 : Déployer la nouvelle architecture

Maintenant pour tester que le déploiement des microservice est fonctionne, on commence par déployer : 

`docker stack deploy -c docker-compose.yml woodytoys`

Une fois déployer on vérifie que tous les services ont bien démarrés : `docker service ls`

### Etape 2 : Test du routage

Ensuite il faut s'assurer que NGINX redirige bien les requêtes vers les bons conteneurs. On va donc utiliser effectuer les requêtes vers ces différents routes, pour s'assurer qu'elles soient fonctionnel : 

**1. Test de la route des produits** : 

`curl -i http://localhost/api/products`

Après exécution on obtient bien un `200 OK`, ce qui prouve que la route est fonctionnel :

![Test de la route des produits](../TP9/pictures/1.%20Test%20route%20produits.png)

**2. Test de la route des utilisateurs** : 

`curl -i http://localhost/api/users`

Ici on a eu un `404 Not Found`, car la route n'existe pas dans les configurations donees, mais cela permet de prouver que la communication s'effectue bien, sinon aurait eu un timeout. 

Et si on nécessaire on vérifiera les logs du conteneur reverse, pour vérifier que les requêtes ont bien été reçus : `docker service logs woodytoys_reverse` 

### Etape 3 : Test avec isolement des services

Ici on va s'assurer, que les services puissent fonctionner de manière, indépendant en simulant une panne. On va pour cela couper le service des utilisateurs, et essayer d'accéder aux produits, pour voir si on arrive toujours à y accéder.

**1. Coupure du service utilisateur**

`docker service scale woody_api-users=0`

**2. Test de l'accès aux utilisateurs**

`curl -i http://localhost/api/users`

On retrouve ici a nouveau le `404 Not Found`, comme avant, ce qui montre que la route fonctionne toujours 

**3. Test de l'accès aux produits** 

`curl -i http://localhost/api/products`

Ici on obtient un `502 Bad Gateway`, ce qui montre que le service est bien éteint, avec le `404`, d'avant cela prouve bien que ça fonctionne toujours même avec ce service éteint. 

![Résultat produits après coupure](../TP9/pictures/1.%20Test%20route%20produits%20après%20coupure.png)

# 2. Communication Asynchrone
## Identification d'un service nécessitant un message broker

*Identifiez, dans les bottlenecks vus précédemment, ceux qui pourraient être améliorés grâce à un Message Broker*

En regardant le code principal python du fichier `main.py`, on a repéré un endroit qui pourrait être amélioré grâce un message broker : 

``` Python
# #### 4. internal Services
def process_order(order_id, order):
    status = woody.make_heavy_validation(order) # <--- CETTE ENDROIT
    woody.save_order(order_id, status, order)
```

Pour l'instant, si un client appelle `/api/orders/do`, l'API appelle `process_order`. Cette fonction lance `make_heavy_validation` qui bloque tout le système pendant plusieurs secondes, le client attend devant une page qui charge.

Afin de pouvoir régler ceci, on va faire en sorte que notre API mettent la commande dans la fille d'attente RabbitMQ, et qu'il réponde "Commande reçue !" instantanément. Cela fera qu'en arrière-plan, un travailleur récupère le message et fait la validation lente.

## Mise à jour du `docker-compose.yml`

Nous mettons à jour notre `docker-compose.yml`, afin de pouvoir ajouter `rabbitmq`, ainsi que le `worker`, qui se chargera de la validation : 

``` YAML
# Le Message Broker
  rabbitmq:
    image: rabbitmq:3-management # La version management inclut une interface web super pratique !
    networks:
      - woodynet
    deploy:
      placement:
        constraints:
          - node.hostname == manager1

  # Le travailleur de l'ombre (Consommateur)
  worker:
    image: gloutamax/woody_api:v2 # On réutilise l'image de l'API car elle contient woody.py
    command: python worker.py # On écrase la commande de lancement par défaut pour lancer notre script
    networks:
      - woodynet
    deploy:
      replicas: 2 # On peut avoir plusieurs travailleurs en parallèle !
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - rabbitmq
      - db
```

## Modification du producteur (l'API Flask)

Dans le fichier de l'API Flask (`main.py`), on importa libraire pika et json avec : `import pika` et `import json` au début d fichier, et on modifie la route de création de commande, pour qu'il utilise RabbitMQ : 

``` Python
@app.route('/api/orders/do', methods=['GET'])
def create_order():
    product = request.args.get('order')
    order_id = str(uuid.uuid4())
    
    # 1. On se connecte à RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    
    # 2. On s'assure que la file existe
    channel.queue_declare(queue='order_queue')
    
    # 3. On prépare le message (en JSON pour que ce soit propre)
    message = json.dumps({'order_id': order_id, 'product': product})
    
    # 4. On poste le message dans la file
    channel.basic_publish(exchange='', routing_key='order_queue', body=message)
    connection.close()
    
    # 5. On répond instantanément au client !
    return f"Your process {order_id} has been created with this product : {product}. It will be processed shortly!"
```

## Création du consommateur (`worker.py`)

Nous créons maintenant le fichier `worker.py` (*que l'on met au même endroit que l'API*), il va tourner en boucle et écouter de RabbitMQ : 

``` Python
import pika
import json
import woody
import time

def callback(ch, method, properties, body):
    # Cette fonction est appelée à chaque fois qu&apos;un message arrive
    data = json.loads(body)
    order_id = data[&apos;order_id&apos;]
    product = data[&apos;product&apos;]

    print(f&quot; [x] Reçu la commande {order_id} pour le produit {product}&quot;, flush=True)

    # On exécute l&apos;opération lente
    status = woody.make_heavy_validation(product)
    woody.save_order(order_id, status, product)

    print(f&quot; [x] Commande {order_id} terminée et sauvegardée !&quot;, flush=True)

print (&quot;Démarrage du worker, recherche de RabbitMQ...&quot;, flush=True)

# Boucle de reconnexion
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=&apos;rabbitmq&apos;))
        print(&quot;Connecté à RabbitMQ avec succès !&quot;, flush=True)
        break # On sort de la booucle si ça a marché
    except Exception as e:
        print(&quot;RabbitMQ n&apos;est pas encore prêt, on patiente 3 secondes...&quot;, flush=True)
        time.sleep(3) # On attend avant de réessayer

channel = connection.channel()

# On déclare la file (au cas où le worker démarre avant l&apos;API)
channel.queue_declare(queue=&apos;order_queue&apos;)

# On dit au worker de consommer la file et d&apos;utiliser la fonction callback
channel.basic_consume(queue=&apos;order_queue&apos;, on_message_callback=callback, auto_ack=True)

print(&apos; [*] En attente de messages...&apos;, flush=True)
channel.start_consuming()
```

*Remarque : Nous avons également importé la bibliothèque `time` afin de pouvoir laisser le temps que le service RabbitMQ, démarre complètement. On a mis une boucle try qui vérifie toutes les 3 secondes si le service est démarré ou non, sinon il revérifie, et attend de nouveau 3 secondes, jusque'à ce que le service soit démarré* 

## Mise à jour des bibliothèques à utiliser 

Il faut modifier le fichier `requirements.txt`, qui indique à python les biothèques à installer et utiliser, pour y ajouter la bibliothèque `pika` :

```
flask
flask-cors
mysql-connector-python
redis
pika
```

## Reconstruction de l'image et mise à jour du docker-compose  

Étant donnée que nous avons modifié le code source de l'image nous devons la reconstruire pour que les nouveaux changements soient prise en compte :

`docker build -t gloutamax/woody_api:v4 .`

Puis on met à jour le `docker-compose.yml`, avec le nom de cette nouvelle image, le fichier ressemble maintenant à celui-ci : 

```YAML
version: "3.9"

services:
  db:
    image: gloutamax/woody_database:latest
    networks:
      - woodynet
    deploy:
      placement:
        constraints:
          - node.hostname == manager1
    cap_add:
      - SYS_NICE
    restart: always
    environment:
      - MYSQL_DATABASE=woody
      - MYSQL_ROOT_PASSWORD=pass

  redis:
    image: redis:alpine
    networks:
      - woodynet
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.hostname == manager1

  api-products:
    image: gloutamax/woody_api:v4
    networks:
      - woodynet
    deploy:
      replicas: 5
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - db
      - redis

  api-users:
    image: gloutamax/woody_api:v4
    networks:
      - woodynet
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - db
      - redis

  api-misc:
    image: gloutamax/woody_api:v4
    networks:
      - woodynet
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - db
      - redis

  front:
    image: gloutamax/woody_front:v4
    networks:
      - woodynet
    deploy:
      replicas: 2

  reverse:
    image: gloutamax/woody_rp:latest
    networks:
      - woodynet
    volumes:
      - ./reverse-proxy/default.conf:/etc/nginx/conf.d/default.conf
    ports:
      - target: 80
        published: 80
        protocol: tcp
        mode: host
    deploy:
      mode: global
    depends_on:
      - front
      - api-products
      - api-users
      - api-misc

  rabbitmq:
    image: rabbitmq:3-management
    networks:
      - woodynet
    deploy:
      placement:
        constraints:
          - node.hostname == manager1

  worker:
    image: gloutamax/woody_api:v4
    command: python worker.py
    networks:
      - woodynet
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.hostname == manager1
    depends_on:
      - rabbitmq
      - db

networks:
  woodynet:
    driver: overlay

configs:
  nginx_config:
    file: ./reverse-proxy/default.conf
```

## Test de la mise en place
### Test du gain de performance

Avant, lorsque'on passait une commande, le terminal restait bloqué à attendre que la `heavy_validation` se termine. On vérifie que ceci sont pris en compte instantanément :

`curl -i "http://localhost/api/orders/do?order=ps5"`

On observe que cela répond instantanément, on a un `200 OK`, et on récupère bien le `UUID` associé à cette commande : 

![Résultat test du gain de performance](../TP9/pictures/2.%20Test%20gain%20de%20performance.png)

### Test du worker

On vérifie que le worker a bien traité la requête en jetant un coup d'oeil aux logs du worker : 

`docker service logs woodytoys_worker`

On retrouve bien les messages, qui indiquent que le `UUID` a été généré, et que la demande a bien été prise en compte : 

![Résultat test du worker](../TP9/pictures/2.%20Test%20du%20worker.png)

### Vérification du résultat

Avec le `UUID` qui a été généré, on va maintenant vérifié que la base de données à bien été mise à jour par le worker une fois le traitement terminé.

`curl -i "http://localhost/api/orders/?order_id=UUID"`

*Note : Il faut remplacer `UUID`, par l'`UUID` obtenus lors du 1er curl*

Et grâce à l'`UUID`, qu'on avait obtenus précédemment, en l'utilisant on retrouve bien la commande, ce qui prouve qu'il a bien été sauvegardé dans la base de donnée : 

![Vérification du résultat](../TP9/pictures/2.%20Vérification%20du%20résultat%20final.png)

### Test de la monté en charge

Pour tester la monté en charge on va exécuter plusieurs requête simultanément, pour voir si l'ensemble des commandes, arrivent à être prises en charge. On fait ceci avec cette commande : 

`for i in {1..5}; do curl "http://localhost/api/orders/do?order=jouet_$i"; echo ""; done`

Et on voit les 5 opérations qui ont été prise en charge, avec succès instantanément, sans ralentissement, ce qui prouve, que le système mis en place est robustesse et est capable de gérer plus traitement simultanément : 

![Résultat test de la monté en charge](../TP9/pictures/2.%20Test%20monté%20en%20charge.png)

# 3. API Gateway
## Mise en place de l'API Gateway

Afin de pouvoir mettre en place l'API Gateway on modifie le fichier de configuration nginx (`default.conf`), on va ajouter 2 nouvelles options :

1. `limit_req_zone` : Pour créer une zone de mémoire qui va retenir les adresses IP des visiteurs et définir la limite stricte
2. `limit_req` : Pour appliquer la limite créer à une route spécifique.

Avec l'applications de ces 2 nouvelles options le fichier est maintenant de cette forme : 

``` Nginx
# 1. LA ZONE DE MÉMOIRE (À mettre TOUT EN HAUT, avant le "server {")
# - $binary_remote_addr : On traque l'adresse IP de l'utilisateur
# - zone=apilimit:10m : On alloue 10 Mo de RAM pour stocker les IPs (suffisant pour des milliers d'IP)
# - rate=60r/m : La limite stricte (60 requêtes par minute, soit 1 par seconde)
limit_req_zone $binary_remote_addr zone=apilimit:10m rate=60r/m;

server {
    listen 80;
    server_name localhost;

    # 2. L'APPLICATION DE LA LIMITE

    location /api/products {
        limit_req zone=apilimit; # <-- On active la limite ici
        proxy_pass http://api-products:5000;
        proxy_set_header Host $host;
    }

    location /api/orders {
        limit_req zone=apilimit; # <-- Et ici
        proxy_pass http://api-users:5000;
        proxy_set_header Host $host;
    }

    location /api/misc {
        limit_req zone=apilimit; # <-- Et là
        proxy_pass http://api-misc:5000;
        proxy_set_header Host $host;
    }

    # Le front-end (on ne limite pas le front, sinon le site ne s'affiche plus !)
    location / {
        proxy_pass http://front:80; 
        proxy_set_header Host $host;
    }
}
```

Et on redémarre le service pour appliquer les changements : 

`docker service update --force woody_reverse`

## Vérification du bon fonctionnement de l'API Gateway

On va envoyer 5 requêtes, simultanément pour voir, si après la 1ère requête celle ci est bloqué avec le code `503 Service Unavailable`, pour tester on utiliser cette commande : 

`for i in {1..5}; do curl -s -o /dev/null -w "Code de retour: %{http_code}\n" http://localhost/api/products; done`

On observe que lors d'une rafale de requêtes simultanées, seule la première requête est traitée par le microservice (`Code 200 OK`). Toutes les requêtes suivantes, arrivant avant l'expiration du délai d'une seconde (*60r/m*), sont bloqué directement par l'API Gateway (NGINX) qui renvoie un code `503 Service Unavailable`. Cela prouve que nos microservices sont protégés contre le spam et les attaques par déni de service, c'est NGINX qui absorbe le tractif malveillant à leur place. 
   
![Résultat de l'API Gateway](../TP9/pictures/3.%20Résultat%20API%20Gateway.png)