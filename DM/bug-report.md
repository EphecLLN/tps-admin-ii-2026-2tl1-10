# Bug report

## Erreurs 502 intermittentes lors de l'accès au service web public dans le cadre d'une panne

## 1. Description du bug

**Nom du groupe :** DAUB Justin, EBERHART Yonas, GROLAUX Baptiste

**Noms des auteurs du bug report :** DAUB Justin, EBERHART Yonas, GROLAUX Baptiste

Nous rencontrons un défaut de tolérance aux pannes (failover) sur notre infrastructure web à haute disponibilité. **Lorsqu'un des serveurs backend tombe en panne, le Load Balancer ne redirige pas l'entièreté de la charge vers le serveur restant fonctionnel.** Par conséquent, si un utilisateur tente d'accéder au service web public à ce moment-là et rafraîchit la page plusieurs fois, ses requêtes échouent de manière intermittente.

- **Résultat normalement attendu :** En cas de panne d'un noeud, le navigateur doit continuer d'afficher la page web "It works!" (Code HTTP 200) à chaque requête, la charge étant gérée de manière transparente par le(s) serveur(s) survivant(s).
- **Résultat obtenu (bug) :** Environ une requête sur deux aboutit à une page blanche affichant "502 Bad Gateway". Les tests en ligne de commande confirment une alternance entre succès (sur le serveur sain) et échec (sur le serveur mort).

![Erreur Page 502](./pictures/Bug%20Report%20-%20Page%20502.png)
![200 et 502 consécutifs](./pictures/Bug%20Report%20-%20200%20et%20502%20consécutifs.png)

## 2. Description du système

L'infrastructure est conteneurisée pour permettre une reproduction fidèle sur une seule machine (VPS de test).

- **Schéma de l’infrastructure :**
  - **Load Balancer :** Nginx (port public 8080).
  - **Backends :** 2 instances Apache (web1 et web2) dans un réseau Docker privé.
- **Logiciels utilisés :** Nginx (latest), Apache httpd (alpine), Docker Compose v2.
  
- **Configurations utilisées :**

**Fichier `docker-compose.yml` :**
```yaml
version: '3.8'

services:
  loadbalancer:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web1
      - web2

  web1:
    image: httpd:alpine
    container_name: web1

  web2:
    image: httpd:alpine
    container_name: web2
```

**Fichier `nginx.conf` :**
``` Nginx
events {}

http {
    upstream backend {
        server web1:80 max_fails=0;
        server web2:80 max_fails=0;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
            proxy_next_upstream off; 
        }
    }
}
```

- **Instructions de lancement :**

    Placez les deux fichiers ci-dessus dans un dossier vide. (Ces fichiers sont aussi trouvables sur le repo de notre groupe dans le Dossier `DM/ex-troubleshooting`, sur la branche `Master`, et non `Main`).

    Lancez l'infrastructure avec : `docker compose up -d`

## 3. Étapes pour reproduire le bug

Pour constater le bug, suivez cette procédure :

1. Vérifiez que les 3 conteneurs sont actifs : `docker ps`.
2. Simulez un crash du deuxième serveur web : `docker stop web2`
3. Exécutez une boucle de test depuis votre terminal : `while true; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080; sleep 1; done`
4. Vous observerez une alternance de codes `200` et `502`. Le Load Balancer continue d'envoyer du trafic vers web2 malgré son arrêt.