import logging
import os
import time
import random
from datetime import datetime, timezone, timedelta
from flask import Flask
from logstash_async.handler import AsynchronousLogstashHandler

app = Flask(__name__)

# Configuration du logger pour envoyer à Logstash
logstash_host = os.environ.get('LOGSTASH_HOST', 'localhost')
logstash_port = int(os.environ.get('LOGSTASH_PORT', 5000))
app_instance_id = os.environ.get('APP_INSTANCE_ID', 'unknown_flask_app')
# Lire le décalage en secondes, par défaut 0
timestamp_offset_seconds = int(os.environ.get('APP_TIMESTAMP_OFFSET_SECONDS', 0))


# Créer un logger standard Python
logger = logging.getLogger(f'flask-logstash-logger-{app_instance_id}')
logger.setLevel(logging.INFO) # Capturer les logs à partir du niveau INFO

# Ajouter le handler Logstash
logstash_handler = AsynchronousLogstashHandler(
    host=logstash_host,
    port=logstash_port,
    database_path=None # Désactiver la mise en cache sur disque pour la simplicité
)
logger.addHandler(logstash_handler)

def log_with_custom_fields(level, message, extra_fields=None):
    # Simuler une latence réseau avant l'envoi du log
    time.sleep(random.uniform(0, 2)) # Délai aléatoire entre 0 et 2 secondes

    # Générer le timestamp de l'événement par l'application
    # Appliquer le décalage simulé
    event_time_utc = datetime.now(timezone.utc) + timedelta(seconds=timestamp_offset_seconds)
            
    base_log_data = {
        'source_app': app_instance_id,
        'event_timestamp': event_time_utc.isoformat() # Format ISO8601 avec Z pour UTC
    }
    if extra_fields:
        base_log_data.update(extra_fields)
            
    if level == logging.INFO:
        logger.info(message, extra=base_log_data)
    elif level == logging.WARNING:
        logger.warning(message, extra=base_log_data)
    elif level == logging.ERROR:
        # exc_info=True ne peut pas être passé directement via 'extra', donc on le gère ici
        # Pour logger.error avec exc_info, il faut appeler logger.error directement.
        # Cette fonction helper est simplifiée pour l'exemple.
        # Pour une solution complète, il faudrait gérer exc_info séparément.
        logger.error(message, extra=base_log_data)
    # ... ajouter d'autres niveaux si nécessaire

@app.route('/')
def index():
    log_with_custom_fields(
        logging.INFO,
        "Page d'accueil visitée.",
        extra_fields={'client_ip': '127.0.0.1', 'endpoint': '/'}
    )
    return f"Hello from {app_instance_id}! Log INFO envoyé."

@app.route('/action')
def action():
    log_with_custom_fields(
        logging.WARNING,
        "Une action sensible a été déclenchée.",
        extra_fields={'user_id': 'dev_user', 'action_name': 'trigger_event'}
    )
    return f"Action effectuée par {app_instance_id}. Log WARNING envoyé."

@app.route('/error')
def error_route():
    try:
        x = 10 / 0
    except ZeroDivisionError as e:
        # Pour les erreurs avec traceback, il est préférable d'appeler logger.error directement
        # car exc_info doit être un argument de la méthode de logging.
        time.sleep(random.uniform(0, 2)) # Latence
        event_time_utc = datetime.now(timezone.utc) + timedelta(seconds=timestamp_offset_seconds)
        log_data = {
            'source_app': app_instance_id,
            'event_timestamp': event_time_utc.isoformat(),
            'error_code': 'DIV_BY_ZERO',
            'context': 'calculation_module'
        }
        logger.error(
            f"Une erreur de division par zéro s'est produite: {str(e)}",
            exc_info=True, # Ajoute automatiquement les informations de traceback
            extra=log_data
        )
    return f"Erreur intentionnelle générée et loguée par {app_instance_id}.", 500

if __name__ == '__main__':
    # Le log de démarrage n'utilisera pas la latence simulée ni le timestamp d'événement pour la simplicité
    startup_message = f"Application Flask {app_instance_id} (avec logs vers ELK) démarrée. Timestamp offset: {timestamp_offset_seconds}s."
    logger.info(startup_message, extra={'source_app': app_instance_id})
    print(startup_message) # Aussi sur la console pour le debug de docker-compose logs
    app.run(host='0.0.0.0', port=8000, debug=False)

