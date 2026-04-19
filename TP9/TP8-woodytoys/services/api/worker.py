import pika
import json
import woody
import time

def callback(ch, method, properties, body):
    # Cette fonction est appelée à chaque fois qu'un message arrive
    data = json.loads(body)
    order_id = data['order_id']
    product = data['product']

    print(f" [x] Reçu la commande {order_id} pour le produit {product}", flush=True)

    # On exécute l'opération lente
    status = woody.make_heavy_validation(product)
    woody.save_order(order_id, status, product)

    print(f" [x] Commande {order_id} terminée et sauvegardée !", flush=True)

print ("Démarrage du worker, recherche de RabbitMQ...", flush=True)

# Boucle de reconnexion
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        print("Connecté à RabbitMQ avec succès !", flush=True)
        break # On sort de la booucle si ça a marché
    except Exception as e:
        print("RabbitMQ n'est pas encore prêt, on patiente 3 secondes...", flush=True)
        time.sleep(3) # On attend avant de réessayer

channel = connection.channel()

# On déclare la file (au cas où le worker démarre avant l'API)
channel.queue_declare(queue='order_queue')

# On dit au worker de consommer la file et d'utiliser la fonction callback
channel.basic_consume(queue='order_queue', on_message_callback=callback, auto_ack=True)

print(' [*] En attente de messages...', flush=True)
channel.start_consuming()



