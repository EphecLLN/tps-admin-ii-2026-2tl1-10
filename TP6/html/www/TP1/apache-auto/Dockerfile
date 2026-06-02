# 1. Image de base
FROM httpd:latest

# 2. Copie des sites web
# On copie le contenu local vers le dossier du serveur dans le conteneur
COPY ./site1/ /usr/local/apache2/htdocs/site1/
COPY ./site2/ /usr/local/apache2/htdocs/site2/

# 3. Copie de notre ficher de config personnaslié 
COPY ./vhosts.conf /usr/local/apache2/conf/vhosts.conf

# 4. Modification du ficher de configuration principal (httpd.conf)
# On ajoute deux lignes à la fin du fichier principal : 
# - Listen 8080 : Pour ouvrir le port
# - Include ... : Pour charger notre fichier vhosts.conf créé plus haut 
RUN echo "Listen 8080" >> /usr/local/apache2/conf/httpd.conf && echo "Include /usr/local/apache2/conf/vhosts.conf" >> /usr/local/apache2/conf/httpd.conf