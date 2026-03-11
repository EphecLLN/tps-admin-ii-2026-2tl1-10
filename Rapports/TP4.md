# # TP4 : Mise en place et sécurisation du DNS public


Noms des auteurs :  DAUB Justin, EBERHART Yonas, GROLAUX Baptiste
Date de réalisation : 02/03/2026

# 1. Installation et configuration de Bind en tant que serveur autoritaire sur un VPS

Pour pouvoir disposer d'un DNS public, il faut avant tout disposer d'un **nom de domaine**.  Nous utiliserons comme domaine parent le domaine **ephec-ti.be**, et chacun de votre groupe disposera de son propre sous-domaine, nommé selon le pattern suivant : ```l[1|2]-[#groupe].ephec-ti.be```. Par exemple, le groupe 2TL1-1 disposera du nom de domaine ```l1-1.ephec-ti.be```.     
## 1.1. Préparation

### Mise en place de l'environnement de travail.  

**Organisation du VPS**

Quelle sera votre hiérarchie de répertoires?  

Chacun des membres du groupe se charge d'essayer de faire les parties du TP faisable et partage ses résultats. Nous avons attribué un des nos VPS pour qu'il soit lié au DNS, nous l'avons fait avec le VPS de Justin. L'idée est ensuite que chacun essaye de déployer le reste des services de son côté. 

**Votre repository Github et son Wiki**

Quelle structure allez-vous donner au repository et au wiki ?  

Pour notre répertoire GitHub, nous allons mettre en place un dossier pour chaque TP, afin d'avoir l'ensemble des configurations qui ont été effectués. On va également prévoir un répertoire rapports, qui contient les fichiers brutes de chacun des TPS. Il seront aussi mis dans l'onglet wiki de GitHub, et seront utilisés sur notre wiki.

**Méthode de configuration**

Quelle procédure de gestion des configurations votre groupe a-t'il choisi ? 

Pour notre groupe nous avons choisis de créer un dossier où nous allons mettre l'ensemble des config dns : 

`mkdir -p ~/dns-projet/config`

A l'intérieur de ce répertoire de config nous créons ensuite les 3 fichiers nécessaires pour le DNS public : 
- `named.conf.options` : Pour les règles globales (désactivation de la récursion pour un DNS public, ports d'écoute, etc.).
- `named.conf.local` : Pour pouvoir déclarer la zone DNS
- `db.mondomaine.com` : Le fichier de zone qui contient tous les enregistrement (A, MX, CNAME...)

### Nom de domaine 

Pour notre groupe le nom de domaine utilisée est : `www.l1-10.ephec-ti.be`, qui redirige vers le VPS de Justin.

## 1.2. Mise en place du serveur autoritaire

### 1.2.1 Premier test du container

Qu'observez-vous comme comportement pré-défini dans ce serveur Bind?  Indiquez vos observations et vos conclusions.

Avec le comportement par défaut dans le serveur Bind, qu'on interroge un domaine publique comme google.com, le serveur répond avec un succès et avec la bonne adresse IP. 

On conclut que par défaut, un serveur Bind9 est pré-configuré pour agir en tant que résolveur récursif avec cache. 

### 1.2.2. Configuration du mode autoritaire 

- Pour chacune des trois fonctionnalités listées plus haut, quelle(s) instruction(s) permet sa mise en oeuvre? 

1. Pour interdire la récursion et la mise en cache : `recursion no;` et `allow-query-cache { none; };`
2. Pour les requêtes acceptées depuis tout l'internet : `allow-query { any; };`
3. Pour définir le serveur en tant que maître : `type master;` et `file "/etc/bind/l1-10.ephec-ti.be.zone`

- Pourquoi interdit-on la récursion ? 

On l'interdit car il est exposé publiquement sur Internet. Si on ne l'interdit pas alors des attaquants peuvent l'utiliser pour faire des attaques DDoS par amplification ou encore de l'empoisonnement de cache (Cache Poisoning).

- Devez-vous configurer une zone inverse pour votre sous-domaine ?  Pourquoi ?  

Non, la zone inverse sert à trouver un nom de domaine à partir d'une adresse IP. Mais vu que l'adresse de notre VPS nous appartient pas directement mais à l'hébergeur (OVH ici), c'est lui qui gère la zone inverse de ce bloc d'IPs. Nous ne gérons que la zone "directe" (`l1-10.ephec-ti.be`).

Reproduisez ici votre fichier ```named.conf``` ainsi que votre fichier de zone.  Indiquez également pour chacun le lien vers la version courante sur le repository.  

*Contenu du fichier `named.conf` :*

```
options {
  directory "/var/cache/bind";
  version "not currently available";
  allow-query { any; };
  allow-query-cache { none; };
  recursion no;

  // Nouvelle ligne pour le support de l'IPv6
  listen-on-v6 { any; };
};

zone "l1-10.ephec-ti.be." {
  type master;
  file "/etc/bind/l1-10.ephec-ti.be.zone";
  allow-transfer { none; };

  // Activation de DNSSEC
  inline-signing yes;
  dnssec-policy default;
};
```

*Contenu du fichier de zone `l1-10.ephec-ti.be.zone` :*

```
$TTL    86400
@       IN      SOA     ns1.l1-10.ephec-ti.be. admin.l1-10.ephec-ti.be. (
                              4         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                          86400 )       ; Negative Cache TTL

@       IN      NS      ns1.l1-10.ephec-ti.be.

ns1     IN      A       91.134.138.155
@       IN      A       91.134.138.155
www     IN      A       91.134.138.155

ns1     IN      AAAA    2001:41d0:305:2100::1:138b
@       IN      AAAA    2001:41d0:305:2100::1:138b
www     IN      AAAA    2001:41d0:305:2100::1:138b
```
**Remarque : Les 3 dernières lignes sont pour l'IPv6, nous décrivons comment nous l'avons mis en place dans l'étape `1.5`**

Faites le bilan de la validation : 
- Quelles commandes avez-vous utilisées? 
  - **Pour interroger le serveur** : La commande principale utilisée est `dig` (ex : `dig @<IP_VPS> www.l1-10.ephec-ti.be`), Le `@` permet de forcer la requête directement sur le serveur DNS plutôt que de passer par le résolveur par défaut du système.
  - **Pour la vérification interne** : `docker logs dns` pour vérifier les messages de démarrage du service Bind 9.

- Quels résultats avez-vous obtenus, et quelles conclusions pouvez-vous en tirer sur le fonctionnement de votre serveur DNS ?  
  - **Résultats** : La commande `dig` a retourné un statut `NOERROR`. Dans la section *ANSWER*, on a bien récupéré l'adresse IP (`91.134.138.155`) que nous avions configurée dans notre ficher de zone. Surtout, les flags de la réponse contenaient `aa` (Authoritative Answer). 
  - **Conclusions** : Ces résultats prouvent que notre serveur BInd9 fonctionne correctement en tant que **serveur faisant autorité** (master) pour notre zone. Il a bien lu notre fichier de zone. La présence du flag `aa` confirme qu'il ne donne pas une réponse trouvée dans un cache en tant que simple résolveur, mais bien la réponse officielle et définitive dont il est le propriétaire. Le serveur accomplit donc parfaitement son rôle principal. 


- Comment avez-vous configuré les logs ? Y avez-vous bien accès ? 
  - **Configuration** : Dans notre architecture basée sur Docker, nous avons laissé le comportement par défaut de Bind 9 qui envoie ses logs vers la sorite standard (stdout/stderr) du conteneur. Il n'a donc pas été nécessaire de configurer un bloc `logging { ... };` complexe dans le fichier `named.conf` pour écrire dans un fichier texte.
  - **Accès** : Oui, nous y avons un accès direct et simplifié depuis l'hôte grâce au moteur Docker. En tapant la commande `docker logs dns`, nous avons pu voir Bind9 démarrer, écouter sur le port 53, et surtout, nous avons pu lire la ligne confirmant le chargement de notre zone : `zone l1-10.ephec-ti.be/IN: loaded serial 1`.

## 1.2.3. Construction d'une image pour votre serveur autoritaire

- Documentez votre Dockerfile. 

``` Dockerfile
FROM internetsystemsconsortium/bind9:9.18

ADD named.conf /etc/bind/named.conf
ADD l1-10.ephec-ti.be.zone /etc/bind/l1-10.ephec-ti.be.zone
RUN chown -R bind:bind /etc/bind/

CMD ["-g", "-c", "/etc/bind/named.conf", "-u", "bind"]
```

- Comment avez-vous validé votre image ? 

D'abord en construisant l'image : 
`docker build -t l1-10-dns .`

Ensuite en supprimant le conteneur précédent : 
`docker rm -f dns`

Puis en démarrant cette nouvelle image personnalisé, tout en reliant le port 53 : 
`docker run -d --name=dns-prod -p 53:53/udp -p 53:53/tcp l1-10-dns`

Pour valider ceci on fait un dig : 
`dig @91.134.138.155 www.l1-10.ephec-ti.be`

## 1.3. Délégation de la zone

- Indiquez ici les deux Resource Records à transférer à la zone parente

- Le **record NS (Délégation)** : `l1-10.ephec-ti.be. IN NS ns1.l1-10.ephec-ti.be.`
- Le **record A (Glue Record)** : `ns1.l1-10.ephec-ti.be. IN A 91.134.138.155`

- Montrez via des screenshots que la délégation fonctionne.
![Dig vers la zone parente ephec-ti.be](/TP4/pictures/1.3%20Délégation.png)  

## 1.4. Validation du serveur autoritaire

- Indiquez le screenshot avec l'état de validation Zonemaster
![Résultat avec Zonemaster](/TP4/pictures/1.4%20Zonemaster.png)
- Expliquez avec vos mots ce que signifie chaque test
  - **System / Basic / Syntax / Consistency (Tout en vert)** : Ces tests vérifient les fondations, et confirment que les DNS répond bien aux requêtes, que la syntaxe du fichier de zone ne contient aucune faute, et que les numéros de série (SOA) sont cohérents.
  - **Connectivity (2 Avertissements oranges)** : Zonemaster vérifie ici la Diversité des AS et la Diversité des préfixes IP. En clair, Internet exige que les serveurs DNS d'un domaine ne soient pas tous au même endroit géographique ou chez le même fournisseur pour éviter les pannes. Vu qu'on a un seul VPS (chez un fournisseur), Zonemaster nous avertit que nous avons un "point de défaillance unique".
  - **Dnssec (A Avertissement orange)** : DNSSEC est une couche de sécurité avancée qui ajoute des signatures cryptographique aux réponse DNS pour éviter le piratage. On ne l'a pas encore configurée, d'où l'avertissement.
  - **Delegation (1 Erreur rouge)** : C'est la seul vraie erreur du test, les standards d'Internet (RFC) exigent qu'un domaine possède au minimum 2 serveurs de noms (un primaire et secodnaire) pour être tolérant aux pannes. Dans le fichier, il n'y a que la déclaration de `ns1`.

- Faites le bilan de cette validation sur votre zone : quels sont les points d'amélioration ?  Si vous pouvez les réalisez, documentez les changements réalisés et montrez bien les screenshots du test de validation Zonemaster avant et après les modifications. 

Le serveur est bien autoritaire est fonctionnel, mais il manque de **redodance** (d'où l'erreur rouge). 

On peut améliorer ceci en mettant en place un autre serveur, mais vu qu'on a pas de 2ème VPS, on va déclarer un `ns2` virtuel qui pointera vers la même adresse IP.

Pour cela on ajoute dans le fichier de zone `l1-10.ephec-ti.be.zone` juste après la la déclaration de `ns1`, la déclaration de `ns2`, ainsi qu'un `@`, le ficher est mainteant de cette forme : 
```
METTRE CONTENU DU FICHER ICI
```

Ensuite on reconstruit l'image Docker : 
``` bash
docker build -t mon-dns-l1-10 .
docker rm -f dns
docker run -d --name=dns -p 53:53/udp -p 53:53/tcp mon-dns-l1-10
```

On refais ensuite le test en ajoutant `ns2.l1-10.ephec-ti.be` dans la liste des serveurs de noms dans les options : 

**METRE RESULTAT ICI** 

## 1.5. Pour aller plus loin [facultatif]

Si vous avez mis en place un des bonus proposés, documentez votre travail ici.

### Mise en place du support IPv6

#### Partie 1 : Trouver l'adresse IPv6

Nous avons mis en place le support de l'IPv6, nous avons d'abord cherché l'adresse IPv6 du VPS avec : 

`ip -6 addr show scope global`

#### Partie 2 : Ajout de l'option IPv6

Une fois trouvé on modifie le fichier de configuration `named.conf`, on y ajoute dans le bloc `options { ... };` la ligne `listen-on-v6` : 

```
options {
  directory "/var/cache/bind";
  version "not currently available";
  allow-query { any; };
  allow-query-cache { none; };
  recursion no;
  
  // NOUVELLE LIGNE : On écoute sur toutes les interfaces IPv6
  listen-on-v6 { any; };
};
```

#### Partie 3 : Ajouts des enregistrements IPv6 dans la zone

On déclare à internet où se trouve le serveur en IPv6, dans le fichier `l1-10.ephec-ti.be.zone`, on ajoute ces nouveaux enregistrement à la fin du ficher de la zone : 

```
ns1     IN      AAAA    2001:41d0:305:2100::1:138b
@       IN      AAAA    2001:41d0:305:2100::1:138b
www     IN      AAAA    2001:41d0:305:2100::1:138b
```

#### Partie 4 : Reconstruction de l'image avec les options IPv6

``` bash
# 1. On rebuild l'image pour prendre en compte le nouveau Serial et les AAAA
docker build -t mon-dns-l1-10 .

# 2. On supprime l'ancien container
docker rm -f dns

# 3. On relance en forçant l'écoute IPv6 (le [::] signifie "toutes les IPs IPv6")
docker run -d \
  --name=dns \
  -p 53:53/udp \
  -p 53:53/tcp \
  -p [::]:53:53/udp \
  -p [::]:53:53/tcp \
  mon-dns-l1-10-2
```

#### Partie 5 : Test de validation de validation IPv6 

On vérifie si il connait l'adresse IPv6 : 

`dig @91.134.138.155 www.l1-10.ephec-ti.be AAAA`

On vérifie si il est capable de répondre si on interroge l'IPv6 : 

`dig @<IPV6_DU_VPS> www.l1-10.ephec-ti.be AAAA`

# 2.  Sécurisation DNSSEC

## 2.1. Génération des clés et signature de la zone

- Documentez les modifications effectuées

Modification du fichier `named.conf`, on y ajoute ces 2 lignes à la fin du ficher dans la partie `zone` :

```
inline-signing yes;
dnssec-policy default;
```

- Après redémarrage de votre serveur, quels changements observez-vous? 

Le redémarrage du serveur est effectué avec l'ensemble de ces commandes : 
``` bash 
docker build -t mon-dns-l1-10 .
docker rm -f dns
docker run -d --name=dns -p 53:53/udp -p 53:53/tcp mon-dns-l1-10
```

Ensuite pour voir ce que Bind fait en arrière-plan au démarrage : 
`docker logs dns`

On va dans les résultat que Bind a généré des clés (KSK et ZSK) et que la zone à été signé

Après on jette un coup d'oeil au nouveau fichier créer à l'intérieur du container :
`docker exec dns ls -al /etc/bind/`

Plusieurs nouveaux fichiers se sont crées :
- Fichiers `.key` et `.private` : Les paires de clés publiques/privés
- Fichier `l1-10-2.ephec.ti.be.zone.signed` : La zone avec toutes les signatures cryptographiques ajoutées. 
- Fichier `.jnl` : Le journal des modifications

Le dernier changement observé est lors du dig : 
`dig @91.134.138.155 www.l1-10.ephec-ti.be +dnssec +multi`

On observe dans la section `ANSWER SECTION`, on observe un nouveau bloc `RRSIG` qui montre la présence de la signature cryptographique. 
## 2.2. Validation de la clé publique via la zone parente

- Documentez la procédure de création du record DS
On cherche d'abord le nom de la clé publique :
`docker exec dns sh -c "ls -l /var/cache/bind/*.key"`

Une fois le nom trouvé on génére le DNS record : 
`docker exec dns dnssec-dsfromkey /var/cache/bind/Kl1-10.ephec-ti.be.+013+23961.key`

- Reproduisez ici votre record DS. 

`l1-10.ephec-ti.be. IN DS 23961 13 2 0BD0E7DB75CA1D774A7EEDF273090535F837F210B1098D51BFF6941E4D7BDF59`

## 2.3. Tester la sécurisation d'une zone DNS

 - Documentez et commentez ici les résultats obtenus en validant votre configuration avec les trois outils mentionnés. 

### 1. Avec DNSSEC Analyzer 
![Résultat avec DNSSEC Analyzer](/TP4/pictures/2.3%20DNSSEC%20Analyzer.png)


Sur ces résultats on observe que notre zone signe correctement ses enregistrements (les RRSIG et DNSKEY sont valides localement, pastilles vertes). Mais comme attendu, l'outil affiche une erreur au niveau de la zone parente `ephec-ti.be` : aucun enregistrement DS n'est trouvé. La chaîne de confiance est donc brisée à ce niveau, ce qui est normal puisque notre hébergeur ne permet pas cet ajout. 

### 2. Avec `DIG`
#### A. Vérification du RRSIG pour www

`dig @91.134.138.155 www.l1-10.ephec-ti.be +dnssec`

Cette requête avec l'option `+dnssec` nous retourne bien l'enregistrement de sa signature cryptographique (RRSIG). Le serveur autoritaire fait donc bien son travail de signature. 

#### B. Récupération de la clé publique (Record DNSKEY)

`dig @91.134.138.155 l1-10.ephec-ti.be DNSKEY +multi`

On a récupéré les clés publiques de notre zone (records DNSKEY). On peut observer 2 clés : la ZSK (Zone Signing Key) qui signe les enregistrements de la zone, et la KSK (Key Signing Key) qui signe les clés ZSK et sert de point d'ancrage avec la zone parente.

#### C. Vérification de la chaîne de confiance (Records DS)

``` bash
dig DS be. +short          # Réussit (renvoie un DS)
dig DS ephec-ti.be. +short # Réussit (renvoie un DS)
dig @ns110.ovh.net DS l1-10-2.ephec-ti.be. +short # ÉCHOUE (Ne renvoie rien)
```

En remontant la chaîne de confiance, on trouve bien les records DS pour la racine, le TLD `.be`, et le domaine `ephec-ti.be`. Cependant en interrogeant le serveur parent (`ns110.ovh.net`) pour notre-sous-domaine `l1-10-2`, aucun record DS n'est retourné. La chaîne de confiance s'arrête ici.

### 3. Avec `delv`

`delv @91.134.138.155 www.l1-10.ephec-ti.be`

Notre commande `delv` ne retourne pas le status `; fully validated`. L'outil `delv` essaie de valider la réponse en remontant jusqu'aux serveurs racines. Puisque le record DS est manquant dans la zone parente `ephec-ti.be`, `delv` ne peut pas authentifier mathématiquement notre clé publique. Il rejette donc la validation, ce qui confirme l'importantce cruciale du DS Record pour l'intégrité globale du DNSSEC. 

## 2.4. Configurer un résolveur pour valider le DNSSEC

- Quelle(s) instruction(s) Bind permettent de contrôler si un résolveur effectue une validation DNSSEC ou non?  

  - `dnssec-validation auto;` : C'est la configuration recommandée. Elle active la validation DNSSEC et utilise automatiquement les clés cryptographiques de la racine d'Internet pour vérifier la chaîne de confiance. 
  - `dnssec-validation yes;` : Active la validation DNSSEC, mais exige que l'adminstrateur configure manuellement les clés de confiance dans le fichier de configuration. 
  - `dnssec-validation no;` : Désactive totalement la vérification des signatures DNSSEC. Le résolveur acceptera les réponses DNS même si les signatures cryptographiques sont fausses ou manquantes. C'est dangereux car cela rend les utilisateurs vulnérables aux attaques par empoisonnement de cache. 


# Pour aller plus loin (facultatif)

Si vous avez réalisé des bonus, documentez-les ici.  

**PAS DE BONUS REALISE ICI**