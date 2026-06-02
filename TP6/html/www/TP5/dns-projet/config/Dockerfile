FROM internetsystemsconsortium/bind9:9.18

ADD named.conf /etc/bind/named.conf
ADD l1-10.ephec-ti.be.zone /etc/bind/l1-10.ephec-ti.be.zone
RUN chown -R bind:bind /etc/bind/

CMD ["-g", "-c", "/etc/bind/named.conf", "-u", "bind"]
