
# TP5 : Configuration du service web public

### Mise en place de l'environnement de travail

**Infrastructure et environnement de travail :**

Pour ce TP5, nous utilisons un environnement Docker pour déployer le service web. L'infrastructure comprend :

- **VPS utilisé :** Un serveur VPS (Virtual Private Server) hébergeant les conteneurs Docker pour le service web.
- **Services déployés :**
  - Serveur web : Nginx (conteneur `web-service`)
  - Serveur PHP : PHP-FPM 8.3 (conteneur `php-service`)
  - Base de données : MariaDB (conteneur `db-service`)

**Organisation des fichiers :**

- **Sur GitHub :** Les fichiers de configuration sont organisés dans le dossier `TP5Baptiste/web/` du repository. Cette structure comprend :
  - `docker-compose.yaml` : Orchestration des services Docker
  - `nginx.conf` : Configuration Nginx avec virtual hosting
  - `dockerfile` : Dockerfile pour le conteneur Nginx
  - `php/dockerfile` : Dockerfile pour le conteneur PHP
  - `www/html/` : Contenu des sites web (HTML et PHP)
  - `woodytoys.sql` : Script d'initialisation de la base de données

- **Sur le VPS :** Les fichiers sont déployés via Docker Compose. Le volume `./www/html` est monté dans les conteneurs web et PHP pour partager le contenu des sites.

# 1. Configuration de base d'un serveur web

**Configuration de base pour le premier site :**

La configuration de base utilise Nginx comme serveur web. Le fichier `nginx.conf` définit :

- Écoute sur le port 80
- Type MIME par défaut
- Format de log personnalisé : `[$host] $remote_addr [$time_local] $status "$request" $body_bytes_sent`
- Logs d'accès sur stdout et erreurs sur stderr (adapté pour Docker)

**Virtual Hosting :**

Deux virtual hosts sont configurés :

1. **www.l1-10.ephec-ti.be** :
   - Racine : `/var/www/html/www`
   - Index : `index.html`
   - Support PHP via FastCGI vers `php-service:9000`

2. **blog.l1-10.ephec-ti.be** :
   - Racine : `/var/www/html/blog/`
   - Index : `index.html`
   - Site statique (pas de PHP)

**Configuration des logs :**

- Format personnalisé incluant l'hôte virtuel, l'adresse IP, la date, le statut HTTP, la requête et la taille de la réponse.
- Logs d'accès dirigés vers stdout pour être visibles dans les logs Docker.
- Logs d'erreur vers stderr.

**Preuve de fonctionnement :**

- Accès à `http://www.l1-10.ephec-ti.be` affiche la page d'accueil avec "Bienvenue sur le site du groupe L1-1".
- Accès à `http://blog.l1-10.ephec-ti.be` affiche le contenu du blog (page statique).
- Les logs Docker montrent les requêtes avec le format personnalisé, incluant l'hôte virtuel.

# 2. Site web dynamique

**Mise en oeuvre du site web dynamique :**

Le site dynamique utilise PHP pour interroger une base de données MariaDB. Le fichier `product.php` :

- Se connecte à la base `woodytoys` sur le conteneur `db-service`
- Exécute une requête SELECT pour récupérer les produits
- Affiche les résultats dans un tableau HTML

Configuration PHP :
- Image : `php:8.3-fpm`
- Extension : `mysqli` installée pour la connexion MySQL
- Communication avec Nginx via FastCGI

Base de données :
- Image : `mariadb`
- Base : `woodytoys`
- Initialisation via `woodytoys.sql` au démarrage du conteneur

**Procédure de validation :**

Scénarios de test :
1. **Accès au site statique :** Vérifier que `www.l1-10.ephec-ti.be` affiche la page HTML.
2. **Accès au blog :** Vérifier que `blog.l1-10.ephec-ti.be` affiche le contenu du blog.
3. **Fonctionnement PHP :** Accès à `www.l1-10.ephec-ti.be/product.php` doit afficher le catalogue des produits depuis la base de données.
4. **Connexion base de données :** Vérifier que les données sont correctement récupérées (5 produits : cubes, yoyo, circuit, arc, maison).
5. **Logs :** Vérifier les logs d'accès pour chaque requête avec le format personnalisé.

**Application de la procédure :**

- Le site statique fonctionne correctement.
- Le blog affiche son contenu (page HTML statique).
- La page PHP `product.php` se connecte à MariaDB et affiche le tableau des produits avec ID, nom et prix.
- Les logs montrent les requêtes avec l'hôte virtuel correct.

**Déploiement Docker Compose :**

Le fichier `docker-compose.yaml` orchestre trois services :

- `db-service` : MariaDB avec volume pour l'initialisation SQL
- `php-service` : PHP-FPM avec volume partagé pour le code
- `web-service` : Nginx avec volume partagé et dépendances vers PHP et DB

Commande de déploiement : `docker-compose up -d`

**Vérification post-déploiement :**

La même procédure de validation s'applique. Après déploiement Docker Compose :
- Tous les services démarrent correctement
- Les sites sont accessibles sur le port 80
- PHP fonctionne et se connecte à la base
- Les logs sont visibles via `docker-compose logs`  
