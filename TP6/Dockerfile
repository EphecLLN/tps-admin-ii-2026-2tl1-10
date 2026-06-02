# Utilisation de l'image officielle Nginx (version stable)
FROM nginx:stable-alpine

# On remplace la configuration par défaut par la nôtre
COPY nginx.conf /etc/nginx/nginx.conf

# Création du dossier pour le VirtualHost
RUN mkdir -p /var/www/html/www/ /var/www/html/blog/

# Installation de certbot et de son plugin Nginx
RUN apk add --no-cache certbot certbot-nginx

# On expose le port 80
EXPOSE 80
