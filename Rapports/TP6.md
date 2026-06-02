# TP6 : Sécurisation du service web public

Noms des auteurs :  DAUB Justin, EBERHART Yonas, GROLAUX Baptiste

Date de réalisation : 16/03/2026

# 2. Sécurisation serveur

Documentez et faites le point ici sur l'état de sécurisation de votre serveur.  

Afin de vérifier, que notre VPS est bien sécurisé, nous avons refait le tour sur toutes les mesures de sécurité qu'on avait mis en place lors du la sécurisation du VPS au `TP3`.

Tout d'abord on a effectué les mises à jour, pour s'assurer d'avoir un système des packages à jour : 

`sudo apt update && sudo apt upgrade -y`

Ensuite nous avons vérifié que notre Pare-feu est toujours bien en place et qu'il autorise pas d'autre ports superflu :

`sudo ufw status`

En parallèle de ceci nous avons également profité pour mettre à jour le docker engine, il a été nécessaire pour effectuer l’installation des images adaptés, ainsi que pour la sécurité. On a procéder à cette mise à jour : 
- En Téléchargent le script de mise à jour officiel docker : 

	`curl -fsSL https://get.docker.com -o get-docker.sh`

- En exécutant le script téléchargé avec les droits administrateurs : 

	`sudo sh get-docker.sh`

- En vérifiant que la mise à jour à bien été appliqué (en vérifiant la version de docker) :

	`docker version`

Une fois cette mise à jour effectué nous en avons profité pour mettre à jour notre docker-compose, pour correspondre aux attentes et s'assurer d'avoir les versions adapté pour la stabilité et la sécurité de toutes nos images : 

``` YAML
services:
  nginx:
    build: .
    ports:
      - "80:80"
    volumes:
      - ./html:/var/www/html
    depends_on:
      - php
      - mariadb
    restart: always

  mariadb:
    image: mariadb:11.1
    env_file:
      - db/root.env
      - db.env
    volumes:
      - ./woodytoys.sql:/docker-entrypoint-initdb.d/woodytoys.sql
    restart: always

  php:
    build: ./php-container
    volumes:
      - ./html:/var/www/html
    env_file:
      - db.env
    restart: always
```

Puis enfin nous avons fait le point sur les ports qui étaient actuellement utilisés : 

`sudo ss -tulpn | grep LISTEN`

Et cet à ce moment que nous avons constaté qu'il y avait la présence d'un port superflu, qui était pourtant non autorisé par le par-feu. Il s'agit du port `5355`, qui correspond sur linux au service `systemd-resolve` qui sert à trouver le nom des machines sur un réseau local sans serveur DNS. Nous avons pas besoin ici, donc pour le désactiver nous avons procédé de cette façon : 
- On a ouvert le fichier `/etc/systemd/resolved.conf`
- Dedans on a décommenté la ligne `#LLMNR=yes` pour la changer en `LLMNR=no`
- Enfin nous avons redémarré le service pour que les modifications soient prise en compte : `sudo systemctl restart systemd-resolved`

Après ceci le port avait bien disparu, il nous restait plus que les ports nécessaires. 

# 3. Sécurisation des données

## 3.1. Isolation de la base de données

- Documentez ici les modifications effectuées sur votre infrastructure pour isoler la base de données.  

Afin de pouvoir isoler la base de données, nous avons crée des réseaux séparé, entre les différents conteneurs, nous avons procédé en adaptant le docker-compose de cette façon : 

``` YAML
services:
  nginx:
    build: .
    ports:
      - "80:80"
    volumes:
      - ./html:/var/www/html
    depends_on:
      - php
    networks:          # <-- NOUVEAU
      - dmz            # <-- NOUVEAU
    restart: always

  mariadb:
    image: mariadb:11.1
    env_file:
      - db/root.env
      - db.env
    volumes:
      - ./woodytoys.sql:/docker-entrypoint-initdb.d/woodytoys.sql
    networks:          # <-- NOUVEAU
      - db_net         # <-- NOUVEAU
    restart: always

  php:
    build: ./php-container
    volumes:
      - ./html:/var/www/html
    env_file:
      - db.env
    networks:          # <-- NOUVEAU
      - dmz            # <-- NOUVEAU
      - db_net         # <-- NOUVEAU
    restart: always

# Déclaration des réseaux à la fin du fichier
networks:              # <-- NOUVEAU
  dmz:                 # <-- NOUVEAU
  db_net:              # <-- NOUVEAU
```

- Etablissez une procédure de validation de l'isolation de la base de données.  

Afin de pouvoir tester l'isolation nous avons effectué différents ping entre les différents conteneurs, il fallait nous assurer que le conteneur PHP puisse communiquer avec celui de MariaDB pour que le PHP puisse communiquer avec la base, et que nginx communique avec PHP. Et enfin le plus important était de vérifier que nginx ne puisse pas communiquer avec nginx pour nous assuré que la base de donnée est bien isolé du web. 

- Test : Nginx vers PHP (Réussi) :
`docker exec -it <nom_du_conteneur_nginx> ping -c 3 php`
- Test : PHP vers MariaDB (Réussi) :
`docker exec -it <nom_du_conteneur_php> php -r "if(@fsockopen('mariadb', 3306)) { echo 'Connexion reussie a MariaDB.' . PHP_EOL; } else { echo 'Echec de la connexion.' . PHP_EOL; }"`
- Test : Nginx vers MariaDB (Échoue normal car on voulait isoler la base de donnée) :
`docker exec -it <nom_du_conteneur_nginx> ping -c 3 mariadb`

*Remarque pour le `Test PHP vers MariaDB` la commande ping n'existait pas, on a donc monté un script rapide, qui affichait `Connexion reussie a MariaDB`, si la communication passait*

## 3.2. Configuration d'un utilisateur non privilégié

- Documentez les modifications effectuées

Afin de pouvoir mettre en place un utilisateur non privilégié, on a modifié le script SQL `woodytoys.sql`, et nous avons ajouté ces lignes à la fin du fichier : 
``` SQL
-- Création de l'utilisateur limité au conteneur 'php'
CREATE USER 'wt-user'@'php' IDENTIFIED BY 'wt-pwd';

-- Attribution des droits de lecture uniquement
GRANT SELECT ON `woodytoys`.* TO 'wt-user'@'php';

-- Application des nouveaux droits
FLUSH PRIVILEGES;
```

Ensuite nous mettons à jour les variables d'environnement dans `db.env` et dans le code php pour pouvoir y mettre le nom et le mot de passe de cet utilisateur non privilégié.

Modification dans `db.env` :
``` 
MARIADB_USER=wt-user
MARIADB_PASSWORD=wt-pwd
```
Modification dans le fichier php : 
``` php
<?php
        // On récupère dynamiquement les informations depuis le fichier db.env
        $dbname = getenv('MARIADB_DATABASE');
        $dbuser = getenv('MARIADB_USER');
        $dbpass = getenv('MARIADB_PASSWORD');
        $dbhost = getenv('MARIADB_HOST');

        // On se connecte (mysqli_connect utilisera désormais wt-user et wt-pwd)
        $connect = mysqli_connect($dbhost, $dbuser, $dbpass) or die("Unable to connect to '$dbhost'");
        mysqli_select_db($connect, $dbname) or die("Could not open the database '$dbname'");
        
        // La requête SELECT fonctionnera car on a donné les droits GRANT SELECT à wt-user
        $result = mysqli_query($connect, "SELECT id, product_name, product_price FROM products");
    ?>
```

Enfin il nous faut réactiver la résolution de nom (DNS) dans MariaDB car par défaut il ne résout pas les noms d'hôtes. POur ce faire nous créons un nouveau fichier `my-resolve.cnf`, et on met ceci dedans : 
``` TOML
[mariadb]
disable-skip-name-resolve=1
```

Et adapte le `docker-compose` pour utiliser le fichier dans le conteneur `mariadb` :
``` YAML
mariadb:
    image: mariadb:11.1
    env_file:
      - db/root.env
      - db.env
    volumes:
      - ./woodytoys.sql:/docker-entrypoint-initdb.d/woodytoys.sql
      - ./my-resolve.cnf:/etc/mysql/conf.d/my-resolve.cnf   # <-- NOUVELLE LIGNE
    networks:
      - db_net
    restart: always
```

Puis on met à jour avec cette nouvelle config on remettant en place l'ensemble des conteurs : 
``` bash
docker compose down -v
docker compose up -d
```

- Proposez une procédure de validation du fait que le serveur web ne peut pas effectuer d'opération dangereuse sur la DB. 

Il suffit juste de vérifier que la page php, soit toujours bien accessible, ce qui prove que c'est sécurisé et bien accessible avec notre utilisateur. 

## 3.3.  Backup de la DB

- Documentez la procédure de backup de votre base de données.

Pour sauvegarder une bakcup de la DB, il faut prévoir un volume pour le conteneur de la DB, on va pour cela ouvrir le fichier `docker-compose` et ajoute un volume pour le répertoire `/var/lib/mysql` : 
``` YAML
services:
  # ... (le service nginx reste inchangé) ...

  mariadb:
    image: mariadb:11.1
    env_file:
      - db/root.env
      - db.env
    volumes:
      - ./woodytoys.sql:/docker-entrypoint-initdb.d/woodytoys.sql
      - ./my-resolve.cnf:/etc/mysql/conf.d/my-resolve.cnf
      - db_data:/var/lib/mysql    # <-- NOUVELLE LIGNE : Montage du volume de données
    networks:
      - db_net
    restart: always

  # ... (le service php reste inchangé) ...

# Tout en bas du fichier, sous la déclaration des networks :
networks:
  dmz:
  db_net:

volumes:                      # <-- NOUVEAU BLOC
  db_data:                    # <-- Déclaration du volume nommé
```

Puis on applique les changements : 
``docker compose up -d`

Ensuite pour tester le backup (export) des données, on extrait le résultat d'un export dans un fichier externe : 
`docker exec web-mariadb-1 mariadb-dump --all-databases -uroot -p"mypass" > /home/justin/backup_bdd.sql`

Puis on regarde ensuite le début du ficher pour s’assurer qu'on repère bien les opérations SQL de notre base :
`head -n 25 /home/justin/backup_bdd.sql`

- Si vous avez réalisé le bonus proposé, documentez-le et prouvez son fonctionnement.    

On ouvre le planificateur de tâches planifiées : 
`crontab -e`

Ensuite on descend tout en bas du fichier, et on ajoute la ligne : 
`0 3 * * * /usr/bin/docker exec web-mariadb-1 mariadb-dump --all-databases -uroot -p"mypass" | gzip > /home/justin/backup_$(date +\%F).sql.gz`

Enfin on sauvegarde et on quitte, et à la fin on vois le message `crontab: installing new crontab`

Et observe la génération de fichiers de backup tout les jours à 3h du matin : 

![Fichiers de backup généré automatiquement à 3h du matin](/TP6/pictures/3.3%20backup.png)

## 3.4. Logs de la DB

- Documentez brièvement comment accéder aux logs de la DB. 

Pour voir les logs de la db il suffit de faire : 
`docker logs <nom_de_votre_conteneur_db>`

On peut si on le souhaite consulter rapidement dernières lignes de cette manière :
`docker logs --tail 50 <nom_de_votre_conteneur_db>`

Et ci nécessaire on peut également suivre les logs en directe de cette manière : 
`docker logs -f <nom_de_votre_conteneur_db>`

# 4. Sécurisation des communications avec HTTPS

## 4.1. HTTPS via un certificat auto-signé

### 4.1.1. Génération du certificat auto-signé avec OpenSSL
On se place dans le dossier avec les fichers de config pour le site web, et on crée un dossier pour les certificats : 
`mkdir certificate`

A l'intérieur de ce dossier on génère la clé privé (.key) ainsi que la demande de signature (.csr) :
`sudo openssl req -nodes -newkey rsa:4096 -keyout certificate/nginx-selfsigned.key -out certificate/nginx-selfsigned.csr`

On répond ensuite aux questions qui s'affichent et on met notre nom de domaine quand demandé : `www.l1-10.ephec-ti.be`

Ensuite on génère l'auto-signature afin de créer le `.crt` : 
`sudo openssl x509 -signkey certificate/nginx-selfsigned.key -in certificate/nginx-selfsigned.csr -req -days 365 -out certificate/nginx-selfsigned.crt`

Il faut ensuite modifier le ficher `docker-compose`, pour le service `nginx`, afin qu'il puisse utiliser le port `443`, nécessaire pour le https, on prend également garde a l'autoriser sur notre par-feu : 
``` yaml
services:
  nginx:
    build: .
    ports:
      - "80:80"
      - "443:443"    # <-- Nouveau port HTTPS
    volumes:
      - ./html:/var/www/html
      - ./certificate:/etc/nginx/ssl  # <-- Nouveau point de montage
``` 

Enfin dans le ficher de configuration nginx, il faut ajouter un bloc serveur qui écoute sur le port 443 avec ces directives : 
``` nginx
listen 443 ssl;
ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
```
 - Montrez par un screenshot la mise en place de votre certificat auto-signé.  
![Fichiers du certifcat auto-signé](/TP6/pictures/4.1%20certificate_file.png)
![Extrait du certificat auto-signé](/TP6/pictures//4.1%20certificate_content.png)

{: .question }
>Que pense votre navigateur du certificat utilisé ?  Pourquoi ? Expliquez la problématique qui est ici mise en évidence.

## Que pense votre navigateur du certificat utilisé ?
Le navigateur va bloque la page et affichage un message d'avertissement critique de sécurité, comme sous la capture ci-dessous :

![Avetissement du certificat](/TP6/pictures/4.1%20Warning.png)

Dans cette stiaution le seul moyen d'accéder au site est de cliquer sur "Avancé" puis "Accepter le risque et poursuivre" pour voir le site.

## Pourquoi ? Expliquez la problématique mis en évidence
Le navigateur bloque le site car le certificat est **auto-signé**, aifn de faire confiance à HTTPS, le navigatuer possède une lise pré-installé d'Autorités de Certification (CA) de confaince (ex : Let's Encrypt, DigiCert, GlobalSign). Ici, on signé le certificat par nous-même, le navigateur voit bien que la connexion est chiffré mais il n'a aucun moyen de vérifié notre identité. 

**Problématique** : Cela met en évidence le reisque d'attaque Man-in-the-Middle. Si par exemple n'importe qui pouvait créer un certificat auto-signé au nom de `banque.com` sans que la navigateur réagissent, un pirate pourrait alors interecpter toutes les communications chiffrées en se faisant passer pour notre banque, c'est donc pour cela que l'authentification est tout aussi importante que la confidentialité.

### 4.1.2. Configuration de Nginx en HTTPS pour le virtualhost ```www```

- Documentez la configuration en HTTPS de nginx.  Montrez via des screenshots bien choisi qu'elle est fonctionnelle.  

On modifie le bloc `server`, pour autorise le 443 pour le https :
``` nginx
events {
}

http {
    # 1. Définition du format personnalisé
    log_format log_per_virtualhost '[$host] $remote_addr [$time_local]  $status '
                                   '"$request" $body_bytes_sent';

    # 2. Application de ce format vers la sortie standard (stdout)
    access_log /dev/stdout log_per_virtualhost;

    # --- Site Principal (WWW) avec HTTPS ---
    server {
        listen 80;
        listen 443 ssl;  # <-- NOUVEAU : On écoute sur le port sécurisé

        server_name www.l1-10.ephec-ti.be;
        
        # J'ai ajouté index.php ici au cas où votre page principale est un PHP
        index index.html index.php; 
        root /var/www/html/www;

        # <-- NOUVEAU : Chemins vers les certificats dans le conteneur
        ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;

        # Le bloc pour PHP (inchangé)
        location ~* \.php$ {
                fastcgi_pass php:9000;
                include fastcgi_params;
                fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        }
    }

    # --- Site Blog (inchangé, reste en HTTP simple) ---
    server {
        listen 80;
        server_name blog.l1-10.ephec-ti.be;
        index index.html;
        root /var/www/html/blog/;
    }
}
```

Et on repère bien le certificat, avec la sécurité : 
![Site sécurisé avec le certifcat](/TP6/pictures/4.1%20Secure_website.png)

## 4.2. Obtention d'un certificat Let's Encrypt pour le site ```www```

Documentez et prouvez la mise en place du certificat let's Encrypt sur vos virtuals hosts.

D'abord on adapate l'image de nginx dans le dockerfile, afin de pouvoir y installer le package certbot, qui nous permettra d'obtenir le certificat :
``` Dockerfile
FROM nginx:latest # (ou la version que vous utilisez)

# Installation de certbot et de son plugin Nginx version Alpine
RUN apk add --no-cache certbot certbot-nginx
```

Puis dans le `docker-compose` on ajoute un nouveau volume, qui va permettre de sauvegarder les certificats : 
``` YAML
nginx:
    build: .
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./html:/var/www/html
      - ./certificate:/etc/nginx/ssl
      - ./letsencrypt:/etc/letsencrypt   # <-- NOUVEAU VOLUME ICI
```

Ensuite on entre dans le conteneur nginx, pour pouvoir y génrer le certificat : 
`docker exec -it <nom_du_conteneur_nginx> sh`

On gnère ensuite le certificat avec : 
`openssl x509 -in /etc/letsencrypt/live/www.l1-10.ephec-ti.be/cert.pem -text -noout`


{: .question}
>1. Examinez les logs dans le fichier ```/var/log/letsencrypt/letsencrypt.log```
	- Trouvez les trois challenges ACME proposés par let's encrypt, et le token utilisé 
	- Trouvez la configuration nginx temporaire utilisée par certbot pour répondre au challenge
	- Quelle est l'URL où se trouve le token sur votre serveur nginx? 
	- Voyez-vous le certificat reçu? De combien de parties se compose-t-il? 
	- Où sont stockés les fichiers du certificat et de la clé privée générées par ```certbot```?
>2. Vérifiez votre configuration ```nginx```: qu'est ce qui a changé? 
>3. Vérifiez si votre site web possède à présent un certificat signé par Let's Encrypt et s'il est accepté par votre navigateur
>4. Examinez le certificat reçu avec l'outil OpenSSL, et identifiez les champs indiquant la signature du CA. 
>5. Vérifiez également le statut HTTPS du second Virtual Host : ```blog.lx-y.ephec-ti.be```.  Que se passe-t-il?  Comment pouvez-vous corriger ça ? 

1. 
- Il y a 3 types de challenges : ``http-01``, ``dns-01`` et ``tls-01``, mais ici certbot a choisi ``http-01``. Le token se trouve à la ligne ``token``
- On observe que le cerbot à crée un bloc avec la ligne : ``location = /.well-known/acme-challenge/T1K9Xtbau9s3EQm6zWLfT1vxUE5KNcZfs8MCrrDRxb0{default_type text/plain;return 200 T1K9Xtbau9s3EQm6zWLfT1vxUE5KNcZfs8MCrrDRxb0.IHfTYp4-VS5g5aD6dTA2uh2WEJl_k-3UXTObTq6EztQ;} # managed by Certbot``
- Let's Encrypt est venu vérifier notre serveur à cette addresse : http://www.l1-10.ephec-ti.be/.well-known/acme-challenge/
- Il se compose de 2 partie, un certificat à qui nous appartient et un autre de Let's Encrypt (qui sert de pont de confiance)
- Tout est stocké dans le dossier ``/etc/letsencrypt/live/www.l1-10.ephec-ti.be/
``

2. Il y a l'ajout d'un noubeau bloc serveur, qui affiche des codes HTTP en fonction de l'état, il y a des options de sécurité qui ont été ajoutés. 

3. Oui il y a bien le cadneas dans le navigateur indiquant que la page est sécurisée, et on voit bien en cliquant sur le cadeans, les détails du certificat et qu'il est bien de letsencrypt.

![Site sécurisée avec un certificat let's encrypt](/TP6/pictures/4.2%20secure_website_let's%20encrypt.png)

4. On obserbe l'identité du signature, au début dans le champ Isuser : ``Issuer: C=US, O=Let's Encrypt, CN=E7``
Ensuite à la toute fin du fichier il y a la signature cyrptographique au champ : ``Signature Algorithm`` qui indique la mthode mathématique utilisée pour signer.

5. Il y a une erreur ``SSL_ERROR_BAD_CERT_DOMAIN``, parce que par défaut si Nginx reçoit une connexion HTTPS pour le site blog mais qu'il n'a pas de configruation SSL spécifique pour lui, il utilise le certificat par défaut.. qui est celui de www. 

![Erreur pour le blog](/TP6/pictures/4.2%20Warning_blog.png)

Comment corriger ? 
Il faut demadner à Cerbot de générer (ou d'étendre) un certificat pour ce deuxième domaine : ``certbot --Nginx -d blog.l1-10.ephec-ti.be``

## 4.3.  Obtention manuelle d'un certificat pour le domaine

Si vous avez réalisé l'obtention d'un certificat wildcard, documentez la procédure et prouvez qu'elle fonctionne sur votre domaine (par ex. via des screenshots). 

Dans un premier terminal, on entre dans le conteneur nginx : `docker exec -it <nom_conteneur> sh`

A l'intérieur on fait la demande du certificat wildcard : 
`certbot certonly --manual --preferred-challenges=dns --email votre@email.com --agree-tos -d "*.l1-10.ephec-ti.be"`


Après ceci **on laisse le terminal ouvert, et n'y touche plus**, on ouvre un deuxième terminal dans le vps, et en ajoute le record, avec le token donnée par le certbot dans le 1er terminal, à la fin du fichier de zone (ceci permet de prouver, que on le domaine bien pour le domaine souhaité) : 

`_acme-challenge   IN   TXT   "LE_TOKEN_DONNÉ_PAR_CERTBOT"`

Avant de valider dans le 1er terminal on vérifie que le token ait bien été valdié : 
`dig +short TXT _acme-challenge.l1-10.ephec-ti.be`

Une fois validé, il nous affiche le token qui avait été généré par le cerbot ce qui prouve que l'enregistremnet a marché.

On adapate ensuite le fichier nignx, pour supprimer les lignes ssl, qui ne sont plus nécessaire avec le nouveau certificat : 
``` nginx
http {
    # ... (vos logs, etc.) ...

    # NOUVEAU : On déclare les certificats au niveau global (http)
    ssl_certificate /etc/letsencrypt/live/l1-10.ephec-ti.be/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/l1-10.ephec-ti.be/privkey.pem;

    server {
        listen 80;
        listen 443 ssl;
        server_name www.l1-10.ephec-ti.be;
        # PLUS BESOIN DES LIGNES SSL ICI !
        # ... reste de la config www ...
    }

    server {
        listen 80;
        listen 443 ssl;
        server_name blog.l1-10.ephec-ti.be;
        # PLUS BESOIN DES LIGNES SSL ICI !
        # ... reste de la config blog ...
    }
}
```

On redméare le service `docker compose restart nginx` puis on valide dans le 1er terminal. Puis on trouve bien sur le site avec `blog` que le site est sécurisé : 

![Blog sécurisée](/TP6/pictures/4.3%20blog_secure.png)