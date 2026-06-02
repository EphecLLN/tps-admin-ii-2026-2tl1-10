# TP3 : Sécurisation des VPS

Noms des auteurs : DAUB Justin, EBERHART Yonas, GROLAUX Baptiste

Date de réalisation : 16/02/2026

## 1. Mise en oeuvre de la procédure de sécurisation proposée par OVH

Dans la TODO list ci-dessous, merci d'indiquer ce qui est réalisé et de documenter les commandes que vous avez utilisées (NOTE : Attention à ne pas mettre d'informations sensibles tel que des mots de passe si votre Wiki est accessible publiquement!.  

Indiquez également soigneusement, pour chaque point, comment vous avez **validé** son implémentation. 

### Connexion à SSH

Avant de commencer à attaquer les points ci-dessous, il faut se connecter à ssh avec la commande : 

`ssh <utilisateur>@<IP_DU_VPS>`

Avec 
- `<utilisateur>` Le nom d'utilisateur de la machine (par défaut debian pour l'utilisateur root)
- `<IP_DU_VPS>` L'adresse IP du VPS, où l'on se connecte

- [X] Mettre à jour le système d'exploitation

Pour mettre à jour le système d'exploitation on va mettre à jour les bibliothèque du système ainsi que la version du système d’exploitation avec l'aide de la commande : 

`sudo apt update && sudo apt upgrade -y`

Avec 
- `sudo apt update` qui met à jour les bibliothèques
- `sudo apt upgrade -y` qui met à jour la version du système d'exploitation (avec l'option -y pour dire oui)

- [X] Modifier le port d'écoute SSH par défaut.

Pour pouvoir modifier le port d'écoute SSH par défaut il faut modifier le ficher de configuration `sshd_config`, avec : 

`sudo nano /etc/ssh/sshd_config`

Ensuite dans le fichier on modifie : 
- `Port 2222` C'est la ligne qui permet de choisir le port sur lequel SSH écoute, par défaut c'est le port 2222, on la remplacé par le port que nous avons choisi. 

- [X] Créer un utilisateur avec des droits restreints

On créé un nouvel utilisateur avec : 

`sudo adduser <nom_utilisateur>`

On lui donne seulement les droits requis avec : 

`sudo usermod -aG sudo <nom_utilisateur>`

On l'ajoute également au groupe docker avec : 

`sudo usermod -aG docker <nom_utilisateur>`


- [X] Désactiver l'accès SSH de l'utilisateur ```root```

Toujours dans le ficher de config `sshd_config` (utilisé précédemment pour changer le port par défaut). 

On modifie : 
- `PermitRootLogin no` On met cette option sur non, afin de pouvoir interdire l'accès au compte root
- `PasswordAuthentication no` Qui interdit les mots de passe et force la clé SSH.

- [X] Configurer le pare-feu : Indiquez les règles choisies (et mettez les à jour au fur et à mesure du semestre)

**Attention : C'est une étape qui doit être réalisé avant de redémarrer SSH, il faut bien que le nouveau port SSH, soit autorisée. Si on redémarre sans donner le droit de connexion au port SSH, la connexion ne sera plus possible car bloqué par le pare-feu.**

Il pour cela taper l'ensemble de commande suivant : 

``` bash
# On installe ufw s'il n'est pas là
sudo apt install ufw
# On autorise ton nouveau port SSH
sudo ufw allow <port_ssh_choisi>/tcp
# On autorise le DNS (port 53) comme demandé
sudo ufw allow 53
# On active le pare-feu
sudo ufw enable
```

Puis on redémarre SSH, pour que les modifications soient prise en compte : 

`sudo systemctl restart ssh`

- [X] Installer Fail2ban et le configurer pour éviter les attaques brute-force sur SSH.  Indiquez les règles choisies (et mettez les à jour au fur et à mesure du semestre)

On installe fail2ban : 

`sudo apt install fail2ban`

On récupère les 2 fichiers de config de fail2ban avec : 

`sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local`

Puis on modifie le ficher de configuration `jail.local`, pour effectuer les config fail2ban : 

`sudo nano /etc/fail2ban/jail.local`

Dans ce fichier nous avons mis la configuration suivante :

``` toml 
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = PORT_CHOISI
backend = systemd
```

On applique ensuite les changements, en redémarrant fail2ban : 

`sudo systemctl restart fail2ban`

Puis on vérifie le bon fonctionnement de fail2ban, en affichant le status : 

`sudo fail2ban-client status sshd` 

## 2. Mise en place de l'authentification SSH par clé

Indiquez si cette étape est mise en place, et documentez vos commandes.  

Cette étape à été réalisé, elle a été réalisé dans la manière suivante : 

### Partie 1 : Génération de la clé 

Depuis l’ordinateur hôte (qui tourne sur windows), on génère d'abord la clé depuis powershell : 

`ssh-keygen -t ed25519 -C "nom_utilisateur@vps-tp"`

Où `nom_utilisateur` est le nom de l'utilisateur en question sur le VPS et `vps-tp` le nom du vps. 

Ensuite, on choisis l'emplacement où stocker la clé sur l'ordinateur hôte, puis si on souhaite en définis une passphrase pour accéder à la clé. 

### Partie 2 : Vérification de l'existence de la clé

Ensuite toujours sur la machine hôte, afin de vérifier que la clé existe on fait : 

`ls $HOME\.ssh\`

On y observe 2 fichiers : 
- `id_ed25519` : La clé privé 
- `id_ed25519` : La clé publique, que l'on va donner au VPS

### Partie 3 : Envois de la clé publique vers le VPS

*Remarque : `ssh-copy-id` n'existe pas par défaut sur windows. On va donc devoir utiliser une commande PowerShell :*

`type $HOME\.ssh\id_ed25519.pub | ssh UTILISATEUR_CREE@IP_VPS "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"`

Cette commande permets la création du dossier `.ssh` sur le VPS et d'y mettre la clé publique.

### Conclusion de cette mise en place

Grâce à la mise en place de cette clé SSH, il n'est désormais plus requis de taper le mot de passe de l'utilisateur à chaque connexion c'est la clé SSH qui permet de nous identifier.

## 3.  Prise en main du VPS

Indiquez sur quel VPS un site web a été déployé. 

Le site web, a été déployé sur le VPS : `91.134.138.155`

### Partie 1 : Autorisation du port web pour le pare-feu

Avant de pouvoir déployer le site sur le VPS, il faut autoriser le port web (port 80) dans le pare-feu ufw :

`sudo ufw allow 80/tcp`

### Partie 2 : Déploiement d'un serveur web avec docker

Docker étant installé dans le vps, on va l'utiliser pour déployer un serveur web avec l'image docker `nginx` : 

`docker run -d --name mon-site -p 80:80 nginx`

Où : 
- `-d` Lance le container en arrière plan
- `-p 80:80` Relie le port 80 du Vps au port 80 du container.

### Partie 3 : Personnalisation de la page web

La Partie 2 permettait de démarrer le serveur avec la page web par défaut de `nginx`, mais nous avons voulus le personnaliser avec l'aide d'un dockerfile, et un index.html.

On a d'abord crée un dossier avec le docker-compose et le index.html :

`mkdir mon-site-web`

Puis on crée les 2 fichiers : 

`touch docker-compose.yml && touch index.html`

Ensuite avec nano on complète les 2 fichiers avec le contenu suivant : 

- Pour le `docker-compose.yml`

``` yaml
version: '3.8'

services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html
    restart: always
```

- Pour le `ìndex.html`

``` html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">

    <title>Mon Super Site VPS</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; }
    </style>
</head>
<body>
    <h1>Bienvenue sur mon VPS Sécurisé !</h1>
    <p>Ce site est hébergé via Docker et Nginx.</p>
    <p>Tout fonctionne parfaitement.</p>
</body>
</html>
``` 

Puis pour le démarrer avec la page web personnalisé, en étant dans le répertoire du docker-compose, on fait : 

`docker compose up -d`