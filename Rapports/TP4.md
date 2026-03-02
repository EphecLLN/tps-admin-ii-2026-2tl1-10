# # TP4 : Mise en place et sécurisation du DNS public


Noms des auteurs :  ....................................
Date de réalisation : ....................................

# 1. Installation et configuration de Bind en tant que serveur autoritaire sur un VPS

Pour pouvoir disposer d'un DNS public, il faut avant tout disposer d'un **nom de domaine**.  Nous utiliserons comme domaine parent le domaine **ephec-ti.be**, et chacun de votre groupe disposera de son propre sous-domaine, nommé selon le pattern suivant : ```l[1|2]-[#groupe].ephec-ti.be```. Par exemple, le groupe 2TL1-1 disposera du nom de domaine ```l1-1.ephec-ti.be```.     
## 1.1. Préparation

### Mise en place de l'environnement de travail.  

**Organisation du VPS**

Quelle sera votre hiérarchie de répertoires?  

**Votre repository Github et son Wiki**

Quelle structure allez-vous donner au repository et au wiki ?  

**Méthode de configuration**

Quelle procédure de gestion des configurations votre groupe a-t'il choisi ? 
### Nom de domaine 

/ 
## 1.2. Mise en place du serveur autoritaire

### 1.2.1 Premier test du container

Qu'observez-vous comme comportement pré-défini dans ce serveur Bind?  Indiquez vos observations et vos conclusions.  
### 1.2.2. Configuration du mode autoritaire 

- Pour chacune des trois fonctionnalités listées plus haut, quelle(s) instruction(s) permet sa mise en oeuvre? 
- Pourquoi interdit-on la récursion ? 
- Devez-vous configurer une zone inverse pour votre sous-domaine ?  Pourquoi ?  


Reproduisez ici votre fichier ```named.conf``` ainsi que votre fichier de zone.  Indiquez également pour chacun le lien vers la version courante sur le repository.  

Faites le bilan de la validation : 
- Quelles commandes avez-vous utilisées? 
- Quels résultats avez-vous obtenus, et quelles conclusions pouvez-vous en tirer sur le fonctionnement de votre serveur DNS ?  
- Comment avez-vous configuré les logs ? Y avez-vous bien accès ? 
## 1.2.3. Construction d'une image pour votre serveur autoritaire

- Documentez votre Dockerfile. 
- Comment avez-vous validé votre image ? 
## 1.3. Délégation de la zone

- Indiquez ici les deux Resource Records à transférer à la zone parente
- Montrez via des screenshots que la délégation fonctionne.  

## 1.4. Validation du serveur autoritaire

- Indiquez le screenshot avec l'état de validation Zonemaster
- Expliquez avec vos mots ce que signifie chaque test
- Faites le bilan de cette validation sur votre zone : quels sont les points d'amélioration ?  Si vous pouvez les réalisez, documentez les changements réalisés et montrez bien les screenshots du test de validation Zonemaster avant et après les modifications. 

## 1.5. Pour aller plus loin [facultatif]

Si vous avez mis en place un des bonus proposés, documentez votre travail ici. 
# 2.  Sécurisation DNSSEC

## 2.1. Génération des clés et signature de la zone

- Documentez les modifications effectuées
- Après redémarrage de votre serveur, quels changements observez-vous? 
## 2.2. Validation de la clé publique via la zone parente

- Documentez la procédure de création du record DS
- Reproduisez ici votre record DS. 

## 2.3. Tester la sécurisation d'une zone DNS

 - Documentez et commentez ici les résultats obtenus en validant votre configuration avec les trois outils mentionnés. 
## 2.4. Configurer un résolveur pour valider le DNSSEC

- Quelle(s) instruction(s) Bind permettent de contrôler si un résolveur effectue une validation DNSSEC ou non?  

# Pour aller plus loin (facultatif)

Si vous avez réalisé des bonus, documentez-les ici.  





