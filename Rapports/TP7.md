# TP7 : Sécurisation du service mail

Noms des auteurs :  DAUB Justin, EBERHART Yonas, GROLAUX Baptiste
Date de réalisation : 23/03/2026

# Introduction

# Environnement de travail et organisation

Documentez brièvement la répartition de vos services sur les différents VPS, et notamment le service mail.  

L’ensemble de tous les services ont été déployés sur le VPS de Justin, les autres VPS, ont plus servis pour s'entraîner à mettre en place, selon différentes configurations, pour ensuite le déployer depuis un seul VPS de notre groupe. Ainsi le PHP et la DB sont parfaitement fonctionnels, avec Nginx, et un service mail fonctionnel, dont nous allons décrire sa mise en place à travers ce rapport. 
 
# 1.  Mise en place du service mail

- Documentez brièvement les étapes principales de la configuration, afin de pouvoir la reproduire en cas de problème.  

## 1. Préparation du répertoire du travail 
On crée un dossier pour ranger tous fichiers de configuration du serveur mail et on se place dedans : 
``` bash
mkdir -p ~/mailserver
cd ~/mailserver
```

## 2. Téléchargement des fichiers officiels    
Une fois l'environnement de travail mis en place on télécharge les fichiers de configurations officiel tout en étant bien dans le répertoire pour les fichiers de configuration du serveur mail : 

``` Bash
DMS_GITHUB_URL="https://raw.githubusercontent.com/docker-mailserver/docker-mailserver/master"
wget "${DMS_GITHUB_URL}/compose.yaml"
wget "${DMS_GITHUB_URL}/mailserver.env"
```

## 3. Paramétrage du `compose.yaml`
On configure le fichier `docker-compose.yaml`, afin de pouvoir y mettre notre nom de domaine :
``` YAML
    hostname: mail.l1-10.ephec-ti.be
```

## 4. Paramétrage du fichier d'environnement `mailserver.env`
Dans ce fichier, on va dire qu'on va utiliser un certifcat let's Encrypt, on modifie pour cela la ligne avec la variable `SSL_TYPE` : 
`SSL_TYPE=letsencrypt`

## 5. Relier le certificat let's Encrypt au serveur mail
Afin de pouvoir assurer que la communication est bien chiffré, nous allons le TLS, en reprenant les certificats TLS qui avait été utilisé pour la sécurisation de Web lors du TP6. 

Pour cela on va à l'intérieur du conteneur Nginx où on avait généré les certificats pour trouver le chemin exact des certificats qui seront utilisé.

Une fois trouvé, on ajoute un nouveau volume, qui va contenir les certificats utilisés pour la sécurisation du Mail
``` YAML
    volumes:
      - ./docker-data/dms/mail-data/:/var/mail/
      - ./docker-data/dms/mail-state/:/var/mail-state/
      - ./docker-data/dms/mail-logs/:/var/log/mail/
      - ./docker-data/dms/config/:/tmp/docker-mailserver/
      - /etc/localtime:/etc/localtime:ro
      - /home/justin/web/letsencrypt:/etc/letsencrypt:ro
```

Il faut ensuite dans le fichier `mailserver.env`, indiquer que l'on utilise un certificat let's encrypt, ainsi que le nom de domaine utiliser : 
```
SSL_TYPE=letsencrypt
SSL_DOMAIN=l1-10.ephec-ti.be
```

## 6. Créer un compte mail
On crée ensuite un compte mail depuis l'intérieur du conteneur mail avec cette commande : 
`docker exec -ti mailserver setup email add admin@l1-10.ephec-ti.be MotDePasse1`

*Note on ajoute aussi un alias Postmaster (qui est obligatoire selon les normes RFC) comme ceci :*
`docker exec -ti mailserver setup alias add postmaster@l1-10.ephec-ti.be admin@l1-10.ephec-ti.be`

## 7. Démarrer le serveur
Une fois toute cette configuration effectué, on lance le serveur depuis notre fichier docker-compose : 
``` Bash
docker compose up -d
```

- Indiquez les tests effectués pour vérifier le bon fonctionnement du service mail, sous forme d'une procédure de validation. 

## 1. Vérification du bon fonctionnement du conteneur
Afin de pouvoir tester le bon fonctionnement du service mail, on a tout d'abord vérifié que le container tourne correctement avec le status `healthy` signifiant que le serveur est UP avec les bonnes configs. On vérifie ceci en regardant l'état des conteneurs : 
`docker container ls`

## 2. Test des adresses mails dans un client mail (Thundebird)
On utilise ensuite un client mail (ici Thunderbird) pour tester si l'envoi et la réception des mails fonctionne.

On configure la première adresse mail `admin@l1-10.ephec-ti.be` de cette manière : 
- **Nom d'utilisateur** : `admin@l1-10.ephec-ti.be`
- **Serveur Entrant (IMAP)** : `mail.l1-10.ephec-ti.be`
  - Port : **993**
  - Sécurité de la connexion : **SSL/TLS**
  - Méthode d'authentification : Mot de passe normal
- **Serveur Sortant (SMTP)** : `mail.l1-10.ephec-ti.be`
  - Port : **587**
  - Sécurité de la connexion : **STARTTLS**
  - Méthode d'authentification : Mot de passe normal

Pour le 2ème compte c'est le même principe on change juste l’identifiant pour mettre `user@l1-10.ephec-ti.be`

- Montrez le résultat de cette première évaluation du service mail avec MXToolbox. 

![1 er résultat MxToolBox](../TP7/pictures/1.%201er%20MxToolBox.png)

### Réponses aux questions

1. Comment sont gérés les utilisateurs?  Via les utilisateurs Unix, un fichier, une DB? 

Ils sont gérés via de simples **fichiers textes**, qui peut être trouvé ici : 
`cat ./docker-data/dms/config/postfix-accounts.cf` 

2. Quel est le format de mailbox utilisé?
   
Le format utilisé est le **Maildir**. Contrairement au format *mbox* (qui met tous les mails dans un seul gros fichier), le format Maildir crée des dossiers (`cur`,`new`,`tmp`) et chaque mail est un fichier indépendant.   

On peut trouver l'ensemble de ces dossiers ici :
`./docker-data/dms/mail-data/l1-10.ephec-ti.be/admin/`

# 2. Sécurisation du service mail


## 2.1. Analyse du chiffrement TLS

### Réponses aux questions

- Indiquez et analyser les ports ouverts pour le chiffrement du mail

On avoir 2 ports pour le chiffrement du mail avec 2 types de TLS : 
  - **Le TLS Explicite (STARTTLS)** : Ici la connexion commence "en clair" (sans sécurité). Le client dit "Bonjour", puis envoie la commande `STARTTLS`. A ce moment-là, ils négocient le chiffrement et la suite de la conversation est sécurisée. Mais le danger est qu'un attaquant sur le réseau peut bloquer la commande `STARTTLS` (attaque "downgrade"), ce qui force les 2 serveurs à continuer en clair.
  - **Le TLS Implicite** : La connexion est chiffrée dès le tout premier octet échangé, sur un port dédié. C'est beaucoup plus sûr car si le chiffrement échoue, la connexion coupe instantanément.

- Analysez votre capture WiresharkDémarrez une capture Wireshark sur votre poste client avant d'envoyer un message depuis un compte de votre domaine, puis de le recevoir.  

**A FAIRE**

- Pour l'envoi, quel est le numéro de port utilisé?  S'agit-il de TLS implicite ou explicite (voir STARTTLS) ?

Pour l'envoi, c'est le **port 587**, c'est le port qui correspond au **TLS explicite (STARTTLS)**

- Même question pour la réception.  

Pour la réception, c'est le **port 993**, c'est le port qui correspond au **TLS implicite** (SSL/TLS direct).

### Bonus
Documentez les éventuels bonus mis en place.

#### Utiliser QUE du TLS Implicite

Afin de pouvoir utiliser uniquement du TLS implicite, il ne faut supprimer STARTTLS pour les client. Cela se réalise de cette manière : 
- **Pour l'IMAP (Réception)** : On ferme le port `143` (en clair/STARTTLS) afin de ne garder que le `993` (Implicite).
- **Pour le SMTP (Envoi par les clients)** : On ferme le port `587` (STARTTLS) et on ouvre le port `465` (le port standard pour le SMTPS en TLS implicite).
- **POINT IMPORTANT** : Il **NE FAUT PAS** fermer le port `25` (qui utilise STARTTLS), c'est un port qui sert à la communication entre serveurs. Interne n'impose pas le TLS implicite entre serveurs, donc si on ferme le port `25`, il ne sera plus possible de recevoir des mails. 

*Comment le mettre en place ?*
Il suffit d'ouvrir notre fichier `compose.yaml`, et de mettre en commentaire les ports dont nous avons plus besoin, comme ceci : 
``` YAML
ports:
      - "25:25"    # SMTP MTA (Obligatoire pour parler avec les autres serveurs - STARTTLS)
      #- "143:143" # On commente/supprime l'IMAP non sécurisé
      #- "587:587" # On commente/supprime le SMTP Submission (STARTTLS)
      - "465:465"  # NOUVEAU : SMTPS (TLS Implicite pour les clients)
      - "993:993"  # IMAPS (TLS Implicite pour les clients)
```

Ensuite lil suffit de relancer, le docker compose, et dans les paramètres du clients il faut changer le port de 587 à **465** et de mettre la sécurité à **SSL/TLS**.

#### Chiffrement de bout en bout avec PGP

Pour pouvoir mettre en place ce chiffrement avec Thunderbird il faut : 

1. Aller dans les **paramètres des comptes**
2. Cliquer sur le **chiffrement de bout en bout** sous le compte `admin`
3. Cliquer sur la flèche vers le bas *(dans l'interface d'envoi)* puis cliquer sur l'option **Joindre ma clé publique**, ou alors dans l'onglet **Sécurité**, on peut cliquer sur **Signer numériquement**.
4. Répéter le même processus pour le compte `user` (on génère une clé pour lui aussi)

**Comment tester ?**

1. Depuis `admin`, on crée un nouveau message pour `user`.
2. Dans la fenêtre de réaction, on clique sur le bouton **Sécurité** (ou l'icône de cadenas) et on choisi "Joindre ma clé publique" (afin que `user` sache comme nous répondre), puis on envoie le mail 
3. Depuis le compte `user`, on ouvre le mail, Thunderbird va enregistrer la clé publique de l'admin *(Si le propose pas atomatiquement on fait un clic droit sur le fichier `.asc`, et on choisis "Importer la clé OpenPGP")*
4. Maintenant, depuis `user`, on clique sur "Répondre", tout en activant le cadenas **Chiffrer** en haut de la fenêtre puis on envoie 
5. *Facultatif* : Pour s'assurer que le cryptage a bien eu lieu, on peut regarder les logs du serveurs ou le fichier brut sur le VPS. On peut y observer que le message n'est qu'un mélange de caractères illisibles, seul Thunderbird peut l'afficher en clair !
   
## 2.2.  Authentification du domaine 

### 2.2.1. L'alignement des records MX-PTR-A 

Documentez et commentez le résultat MXToolbox de cette étape.  

![2ème résultat MXToolbox](../TP7/pictures/2.2.1%202ème%20MxToolBox.png)

- Les 2 lignes vertes en bas du tableau confirment que c'est la mise en place des records est un succès

### 2.2.2. SPF

- Documentez et commentez le résultat MXToolbox de cette étape.  

![Résultat SPF](../TP7/pictures/2.2.2%20Résultat%20SPF.png)

- Indiquez les résultats de l'envoi d'un mail vers une adresse extérieure.  

**A FAIRE**

### 2.2.3. DKIM

- Documentez brièvement les étapes de mise en place du DKIM. 

Afin de pouvoir mettre en place le DKIM, on va d'abord avoir besoin de la clé de génération, qui se génère de cette manière : 
`docker exec -it mailserver setup config dkim`.

Une fois que ces clés ont été généré il nous faut maintenant récupérer la clé publique. Dans le cas de notre configuration dans les volumes partagés, on affiche le contenu avec cette commande : 

`cat ./docker-data/dms/config/opendkim/keys/l1-10.ephec-ti.be/mail.txt`

Dedans il faut récupérer un texte du type : 

`mail._domainkey IN TXT ( "v=DKIM1; h=sha256; k=rsa; " "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AM... )`

Ensuite on copie le texte que nous avons récupéré, pour le mettre dans le fichier de notre zone DNS, qui est par exemple de cette forme : 

`mail._domainkey IN TXT "v=DKIM1; h=sha256; k=rsa; p=TA_TRES_LONGUE_CLE_PUBLIQUE_ICI"`

- Validez cette configuration en montrant un en-tête de mail

**A FAIRE**

- Montrez et commentez le résultat de l'analyse DKIM Validator. 

![Résultat DKIM Validator](../TP7/pictures/2.2.4%20score%20spamassasin-3.png)

### 2.2.4. DMARC

- Documentez brièvement la mise en place du DMARC et commentez le résultat MXToolbox obtenu.  

Le DMARC se met tout simplement en place, en ajoutant une ligne pour DMARC à la fin du fichier de zone, comme ceci : 

`_dmarc  IN      TXT     "v=DMARC1; p=none; rua=mailto:admin@l1-10.ephec-ti.be;"`

![Résultat DMARC](../TP7/pictures/2.2.4%20Résultat%20DMARC.png)

**A COMMENTER ET A VERIFIER**

- Montrez le score SpamAssassin et commentez-le.  Comment l'optimiser? 

Dans notre cas on a obtenus un score de 0.208, ce qui représente un très bon score (l'objectif est d'avoir le score le plus faible possible, voir un score négatif). La raison pour laquelle nous n'avons pas 0 mais 0.2 est dû au fait que le mail de test qui a été envoyé ici, est un mail très court, ne contenant pas de vrai sujet ou de formatage HTMl (cela fait que ça ajoute des micro-pénalités appelées `MISSING_SUBJECT` ou `EMPTY_MESSAGE`).

![Résultat 1 de spamassassin](../TP7/pictures/2.2.4%20score%20spamassasin-1.png)
![Résultat 2 de spamassassin](../TP7/pictures/2.2.4%20score%20spamassasin-2.png)
![Résultat 3 de spamassassin](../TP7/pictures/2.2.4%20score%20spamassasin-3.png)

Afin d'optimiser le score SpamAssassin il faut : 
1. Avoir un SPF, DKIM et DMARC valides (ce qui a été fait au cours de cette étape `2.2`)
2. Avoir un PTR (Reverse DNS) valide qui pointe vers le domaine
3. Éviter d'envoyer des mails vides ou cotenant juste un mot comme "test". Un vrai mail avec des phrases bien construire, un sujet clair et une signature textuelle a un meilleur score.
4. Ne pas avoir son IP sur des lites noires (Black lists). 

## 2.3. Filtrage du spam

- Documentez brièvement l'activation et la configuration de SpamAssassin.  

Le conteneur que nous avons mis en place pour le serveur web, à déjà tout ce qu'il faut pour utiliser SpamAssassin. Il faut l’activer en en modifiant notre fichier environment du serveur mail `mailserver.env

`nano mailserver.env`

Dedans on cherche la ligne `ENABLE_SPAMASSASSIN=0` et on remplace le `0` par un `1`, puis on sauvegarde les modifications. 

Il ne reste plus qu'a redémarrer, en relançant le dockercompose afin que les modification soient prises en compte : 

``` bash
docker compose down
docker compose up -d
```

- Validez son fonctionnement via la réception d'un email valide

En écrivant un mail normal, très court et avec un objet très court, le mail arrive correctement directement dans la boîte principal. Si on regarde le code source du message reçu il n'y a pas de trace de SpamAssassin. Cela est dû au fait que SpamAssassin ne considère par ce message comme un spam, et vu qu'il est très court, il n'affiche pas des lignes concernant le spam dans le code source. 

- Validez son fonctionnement via la réception d'un email suspect

C'est avec un mail suspect que l'on va voir SpamAssassin à l'action. On a écrit un mail contenant une chaîne de caractère tous mélangés qui est appelée ici le **GTUBE**, une chaîne de caractère volontairement étrange qui est utilisé pour tester le bon fonctionnement du système antispam. Ici c'est sans appel, dès la réception du mail, il est directement placé dans les spams. Cette fois-ci si on regarde le code source pour ce mail, on observe bien des traces de SpamAssassin, avec des lignes qui commencent par `X-Spam`. Et on observe un score très élevée, ce qui est indique que le mail est détecté comme étant du spam. 

![Mail étant détecté comme du spam](../TP7/pictures/2.3%20Mail%20spam.png)

# 3. Serveur mail secondaire (bonus)
Si vous avez mis en place un serveur mail secondaire, documentez la configuration choisi