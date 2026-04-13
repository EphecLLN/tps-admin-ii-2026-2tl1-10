FROM ubuntu/bind9

# On écrase la config par défaut avec celle du pc hôte 
COPY named.conf.options /etc/bind/named.conf.options

# On déclare les ports 
EXPOSE 53/udp
EXPOSE 53/tcp