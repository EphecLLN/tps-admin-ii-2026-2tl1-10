import uuid
from datetime import datetime
import redis  # <-- AJOUT : Il faut importer la librairie !

from flask import Flask, request
from flask_cors import CORS

import woody

app = Flask('my_api')
cors = CORS(app)

# <-- MODIFICATION : On décommente la ligne et on ajoute decode_responses=True pour avoir du texte propre
redis_db = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)


@app.get('/api/ping')
def ping():
    return 'ping'


# ### 1. Misc service ### 
@app.route('/api/misc/time', methods=['GET'])
def get_time():
    return f'misc: {datetime.now()}'


@app.route('/api/misc/heavy', methods=['GET'])
def get_heavy():
    name = request.args.get('name')
    
    # On cherche d'abord la réponse dans le cache Redis
    cached_result = redis_db.get(f"heavy_{name}")
    
    if cached_result is not None:
        # Si on l'a trouvée, on la renvoie direct (Ultra rapide)
        return f'{datetime.now()}: {cached_result} (from cache)'
    
    # Si elle n'y est pas, on lance le calcul très lent...
    r = woody.make_some_heavy_computation(name)
    
    # ...puis on sauvegarde le résultat dans Redis pour 60 secondes !
    redis_db.setex(f"heavy_{name}", 60, r)
    
    return f'{datetime.now()}: {r}'


# ### 2. Product Service ###
@app.route('/api/products', methods=['GET'])
def add_product():
    product = request.args.get('product')
    woody.add_product(str(product))
    return str(product) or "none"


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    return "not yet implemented"


@app.route('/api/products/last', methods=['GET'])
def get_last_product():
    # On cherche dans le cache
    cached_last = redis_db.get("last_product")
    
    if cached_last is not None:
        return f'db: {datetime.now()} - {cached_last} (from cache)'

    # Si ce n'est pas en cache, on fait la requête lente à la BDD
    last_product = woody.get_last_product()  
    
    # On met en cache pour 10 secondes (la durée dépend du besoin métier)
    redis_db.setex("last_product", 10, last_product)
    
    return f'db: {datetime.now()} - {last_product}'


# ### 3. Order Service
@app.route('/api/orders/do', methods=['GET'])
def create_order():
    product = request.args.get('order')
    order_id = str(uuid.uuid4())
    process_order(order_id, product)
    return f"Your process {order_id} has been created with this product : {product}"


@app.route('/api/orders/', methods=['GET'])
def get_order():
    order_id = request.args.get('order_id')
    status = woody.get_order(order_id)
    return f'order "{order_id}": {status}'


# #### 4. internal Services
def process_order(order_id, order):
    status = woody.make_heavy_validation(order)
    woody.save_order(order_id, status, order)


if __name__ == "__main__":
    woody.launch_server(app, host='0.0.0.0', port=5000)
