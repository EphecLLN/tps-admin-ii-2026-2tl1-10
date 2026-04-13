# Commandes Docker Compose Utiles 

## 1. Démarrer et Arrêter (Le cycle de vie)

C'est la base pour lancer ton infrastructure et la couper proprement.

**Lancer les services en arrière-plan (Détaché) :**

``` Bash
docker-compose up -d
```
*C'est LA commande à utiliser. Le -d (detach) te rend la main sur le terminal une fois les conteneurs lancés. Si tu l'oublies, tu resteras bloqué sur les logs et si tu fais Ctrl+C, ça coupera tes serveurs.*

**Arrêter ET supprimer les conteneurs/réseaux liés :**

``` Bash
 docker-compose down
```

*Très utile si tu as fait une grosse erreur dans ton docker-compose.yml et que tu veux repartir sur une base propre (attention, ça ne supprime pas les volumes par défaut).*

**Appliquer une modification de configuration :**

``` Bash
docker-compose up -d
```

*Astuce : Si tu modifies ton fichier docker-compose.yml, pas besoin de faire down puis up. Relance juste up -d, Docker va détecter les changements et ne recréer que les conteneurs impactés.*

**Redémarrer un service spécifique :**
``` Bash
docker-compose restart nom_du_service
```

*Utile si tu as modifié un fichier de configuration (comme un fichier de conf Nginx ou DNS) monté en volume et que tu as besoin que le service le prenne en compte.*

## 2. Le Débogage (Pour sauver ton interro)

Si ça ne marche pas du premier coup, ces commandes te diront pourquoi au lieu de chercher à l'aveugle.

**Vérifier l'état des conteneurs :**

``` Bash
docker-compose ps
```

*Regarde la colonne "State". Si c'est "Up", tout va bien. Si c'est "Exit", ton conteneur a crashé, et il faut regarder les logs.*

**Lire les logs en direct (Le Saint Graal) :**

``` Bash
docker-compose logs -f nom_du_service
```

*Le -f (follow) permet de voir les logs s'afficher en temps réel. Indispensable pour voir pourquoi un service web refuse de se lancer ou pourquoi un mail est rejeté.*

**Rentrer à l'intérieur d'un conteneur qui tourne :**

``` Bash
docker-compose exec nom_du_service sh
```

*(Ou bash au lieu de sh selon l'image). Cela te permet d'ouvrir un terminal directement dans ton conteneur web ou mail pour vérifier si un fichier est bien à sa place ou faire un ping depuis l'intérieur.*

## 3. Nettoyage d'urgence (Le bouton panique)

**Tout raser (y compris les données) :**

``` Bash
docker-compose down -v
```

*Le -v supprime aussi les volumes. À n'utiliser que si tu as totalement pollué tes données de test (ex: base de données corrompue) et que tu veux un "reset d'usine" de ton service.*

# Commandes du fichiers docker-compose

## 1. Les blocs de premier niveau

Un fichier Compose est divisé en quatre grandes sections :

- `version` : Définit la version de la syntaxe (ex: '3.8').

- `services` : C'est ici que tu définis tes conteneurs (ton serveur web, ta DB, etc.). 90% de ton travail sera ici.

- `networks` : Pour isoler tes services ou les faire communiquer.

- `volumes` : Pour rendre les données persistantes (éviter de tout perdre au redémarrage).

## 2. Focus sur la section `services`

Chaque service possède ses propres paramètres. Voici les plus fréquents pour un exercice Web ou Mail :

- `image` : Le nom de l'image Docker à utiliser (ex: `nginx:latest`,`postfix`).

- `container_name` : Donne un nom fixe au conteneur (pratique pour le débug).

- `ports` : Fait le lien entre le VPS et le conteneur `[Port_Hôte]:[Port_Conteneur]`

	- Exemple : `8080:80` (le site sera sur le port 8080 de ton IP).

- `volumes` : Lie un dossier du VPS à un dossier interne au conteneur.

	- Exemple : `./html:/usr/share/nginx/html`

- `environment` : Définit des variables (mots de passe, config spécifique).

- `networks` : Liste les réseaux auxquels le service appartient.

- `depends_on` : Indique qu'un service doit démarrer après un autre (ex: le web après la DB).

### Conseils
 
1. **L'indentation :** Toujours utiliser des **espaces** (souvent 2), **jamais de tabulations**. le docker-compose est très sensible
2. **Les listes :** Quand tu as plusieurs éléments (comme dans `ports` ou `volumes`), on utilise un tiret `-` suivi d'un espace.
3. **Les guillemets :** Pour les ports comme `80:80`, il est recommandé de les mettre entre guillemets `'80:80'` pour éviter que YAML ne les interprète parfois comme des nombres en base 60.

