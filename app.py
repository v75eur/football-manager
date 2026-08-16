from flask import Flask, send_file, send_from_directory
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='.')

# ===== ROUTES PRINCIPALES =====
@app.route('/')
def index():
    return send_file('accueil/index.html')

@app.route('/accueil/<path:path>')
def accueil_files(path):
    return send_from_directory('accueil', path)

@app.route('/session/charger')
def session_charger():
    return send_file('session/charger.html')

@app.route('/jeu')
def jeu():
    return send_file('jeu/index.html')

# ===== API =====
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    pseudo = data.get('pseudo')
    email = data.get('email')
    whatsapp = data.get('whatsapp')
    password = data.get('password')
    country = data.get('country')

    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)

    # Vérifier si le joueur existe déjà
    filepath = f"data/{pseudo}.FMTK"
    if os.path.exists(filepath):
        return jsonify({'success': False, 'message': 'Ce pseudo existe déjà'}), 400

    # Créer le fichier du joueur
    player_data = {
        'version': '1.0',
        'pseudo': pseudo,
        'email': email,
        'whatsapp': whatsapp,
        'password': password,
        'country': country,
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat(),
        'player_id': str(uuid.uuid4()),
        'equipe': {
            'nom': '',
            'couleurs': {},
            'drapeau': '',
            'stade': '',
            'terrain': 'style1_classique.html',
            'joueurs': [],
            'tactique': {},
            'stats': {
                'matchs_joues': 0,
                'victoires': 0,
                'defaites': 0,
                'nuls': 0
            }
        },
        'budget': 50000000,
        'transferts': {'achetes': [], 'vendus': []},
        'historique': {'matchs': []}
    }

    with open(filepath, 'w') as f:
        json.dump(player_data, f, indent=2)

    return jsonify({'success': True, 'message': 'Inscription réussie !', 'player': player_data})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    pseudo = data.get('pseudo')
    password = data.get('password')

    filepath = f"data/{pseudo}.FMTK"
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': 'Joueur non trouvé'}), 404

    with open(filepath, 'r') as f:
        player_data = json.load(f)

    if player_data.get('password') != password:
        return jsonify({'success': False, 'message': 'Mot de passe incorrect'}), 401

    player_data['last_login'] = datetime.now().isoformat()
    with open(filepath, 'w') as f:
        json.dump(player_data, f, indent=2)

    return jsonify({'success': True, 'message': f'Bienvenue {pseudo} !', 'player': player_data})

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_file(path)
    return "Fichier non trouvé", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
