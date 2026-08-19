from flask import Flask, send_file, send_from_directory, request, jsonify
import os
import json
import uuid
import hashlib
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
app.secret_key = 'dev-secret-key'
CORS(app)

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# ===== ROUTES PRINCIPALES =====
@app.route('/')
def index():
    return send_file('accueil/index.html')

@app.route('/dashboard')
def dashboard():
    return send_file('dashboard.html')

@app.route('/session/charger')
def session_charger():
    return send_file('session/charger.html')

@app.route('/equipe/creer')
def equipe_creer():
    return send_file('equipe/creer.html')

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename)

# ===== API REGISTER =====
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        pseudo = data.get('pseudo', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        country = data.get('country', '')

        if not pseudo or not email or not password:
            return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires'}), 400

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Ce pseudo existe déjà'}), 400

        player_data = {
            'version': '1.0',
            'pseudo': pseudo,
            'email': email,
            'country': country,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'created_at': datetime.now().isoformat(),
            'player_id': str(uuid.uuid4()),
            'equipe': {
                'nom': '',
                'division': '',
                'pays': '',
                'stade': '',
                'couleurs': '#FFD700 / #003366',
                'joueurs': [],
                'stats': {'matchs': 0, 'victoires': 0, 'defaites': 0, 'nuls': 0, 'buts_marques': 0, 'buts_encaisses': 0},
                'transferts': {'budget': 50000000, 'joueurs_achetes': [], 'joueurs_vendus': []},
                'tactique': {'formation': '4-3-3'}
            }
        }

        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)

        return jsonify({'success': True, 'message': 'Inscription réussie !', 'pseudo': pseudo})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== API LOGIN =====
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        pseudo = data.get('pseudo', '').strip()
        password = data.get('password', '').strip()

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Compte inexistant'}), 404

        with open(filepath, 'r') as f:
            player_data = json.load(f)

        if player_data.get('password') != hashlib.sha256(password.encode()).hexdigest():
            return jsonify({'success': False, 'message': 'Mot de passe incorrect'}), 401

        return jsonify({'success': True, 'message': 'Connexion réussie', 'pseudo': pseudo})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== DOWNLOAD =====
@app.route('/download/<pseudo>')
def download_file(pseudo):
    filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': 'Fichier non trouvé'}), 404
    return send_file(filepath, as_attachment=True, download_name=f"{pseudo}.FMTK")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ===== API JOUEURS =====
@app.route('/api/players/<pseudo>')
def get_player_data(pseudo):
    """Récupère toutes les données d'un joueur pour le popup"""
    try:
        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Joueur non trouvé'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraire les infos du joueur
        equipe = data.get('equipe', {})
        stats = equipe.get('stats', {})
        transferts = equipe.get('transferts', {})
        
        player_info = {
            'pseudo': data.get('pseudo', ''),
            'club': equipe.get('nom', 'Non défini'),
            'division': equipe.get('division', ''),
            'pays': equipe.get('pays', ''),
            'stade': equipe.get('stade', ''),
            'couleurs': equipe.get('couleurs', '#FFD700 / #003366'),
            'budget': transferts.get('budget', 0),
            'joueurs': equipe.get('joueurs', []),
            'stats': stats,
            'created_at': data.get('created_at', ''),
            'last_login': data.get('last_login', ''),
            'player_id': data.get('player_id', '')
        }
        
        return jsonify({'success': True, 'player': player_info})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
import json
import gzip

def get_club_players(club_name):
    """Charge uniquement les joueurs d'un club spécifique"""
    try:
        # Essayer d'abord le fichier compressé
        filepath = 'data/players/all_players_complete.json.gz'
        if os.path.exists(filepath):
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(club_name, [])
        
        # Sinon le fichier normal
        with open('data/players/all_players_complete.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(club_name, [])
    except:
        return []

def search_players(query):
    """Recherche des joueurs sans tout charger en mémoire"""
    results = []
    try:
        filepath = 'data/players/all_players_complete.json.gz'
        if os.path.exists(filepath):
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
                for club, joueurs in data.items():
                    for joueur in joueurs:
                        if query.lower() in joueur.get('nom', '').lower():
                            results.append({
                                'nom': joueur['nom'],
                                'club': club,
                                'poste': joueur.get('poste', ''),
                                'note': joueur.get('note', 0)
                            })
                            if len(results) >= 20:
                                return results
    except:
        pass
    return results

# ===== PAGE DE GESTION DES SAUVEGARDES =====
@app.route('/saves')
def saves_manager():
    """Page de gestion des sauvegardes"""
    try:
        return send_file('saves_manager.html')
    except Exception as e:
        return f"Erreur: {e}", 404
