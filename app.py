from flask import Flask, send_file, send_from_directory, request, jsonify
import os
import json
import uuid
import hashlib
from datetime import datetime
from flask_cors import CORS
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder='.')
app.secret_key = 'dev-secret-key-change-in-production'
CORS(app)

# ===== DOSSIER DATA LOCAL =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

print(f"📁 DATA_DIR: {DATA_DIR}")

# ===== BACKUP MANAGER =====
try:
    from backend.backup_manager import BackupManager
    backup_manager = BackupManager(repo_name='v75eur/football-manager-backups')
    USE_GITHUB_BACKUP = True
    print("✅ BackupManager chargé")
except Exception as e:
    USE_GITHUB_BACKUP = False
    print(f"⚠️ BackupManager non disponible: {e}")

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

# ===== API VERIFY =====
@app.route('/api/verify', methods=['POST'])
def verify_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Aucun fichier envoyé'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Fichier vide'}), 400
        
        # Lire le contenu du fichier
        content = file.read().decode('utf-8')
        data = json.loads(content)
        
        # Vérifier les champs obligatoires
        if 'pseudo' not in data or 'player_id' not in data:
            return jsonify({'success': False, 'message': 'Fichier invalide (champs manquants)'}), 400
        
        # Vérifier la version
        if data.get('version') != '1.0':
            return jsonify({'success': False, 'message': 'Version non compatible'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Fichier valide',
            'pseudo': data.get('pseudo'),
            'player_id': data.get('player_id')
        })
        
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'Fichier JSON invalide'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ===== API REGISTER =====
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        pseudo = data.get('pseudo', '').strip()
        email = data.get('email', '').strip()
        whatsapp = data.get('whatsapp', '').strip()
        password = data.get('password', '').strip()
        country = data.get('country', '')

        if not pseudo or not email or not password:
            return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Mot de passe trop court (6 caractères min)'}), 400

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        
        if os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Ce pseudo existe déjà'}), 400

        # Vérifier email unique
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.FMTK'):
                try:
                    with open(os.path.join(DATA_DIR, filename), 'r') as f:
                        existing = json.load(f)
                        if existing.get('email') == email:
                            return jsonify({'success': False, 'message': 'Cet email est déjà utilisé'}), 400
                except:
                    pass

        player_data = {
            'version': '1.0',
            'pseudo': pseudo,
            'email': email,
            'whatsapp': whatsapp,
            'country': country,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
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

        # Sauvegarde locale
        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)

        # Sauvegarde GitHub
        if USE_GITHUB_BACKUP:
            try:
                backup_manager.backup_player(pseudo, player_data)
                print(f"✅ Sauvegardé sur GitHub: {pseudo}.FMTK")
            except Exception as e:
                print(f"⚠️ Erreur GitHub: {e}")

        return jsonify({
            'success': True,
            'message': 'Inscription réussie !',
            'pseudo': pseudo,
            'player_id': player_data['player_id']
        })

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ===== API LOGIN =====
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        pseudo = data.get('pseudo', '').strip()
        password = data.get('password', '').strip()

        if not pseudo or not password:
            return jsonify({'success': False, 'message': 'Pseudo et mot de passe requis'}), 400

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Compte inexistant'}), 404

        with open(filepath, 'r') as f:
            player_data = json.load(f)

        hashed = hashlib.sha256(password.encode()).hexdigest()
        if player_data.get('password') != hashed:
            return jsonify({'success': False, 'message': 'Mot de passe incorrect'}), 401

        player_data['last_login'] = datetime.now().isoformat()
        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)

        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'pseudo': pseudo,
            'player_id': player_data.get('player_id')
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ===== DOWNLOAD =====
@app.route('/download/<pseudo>')
def download_file(pseudo):
    try:
        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Fichier non trouvé'}), 404
        return send_file(filepath, as_attachment=True, download_name=f"{pseudo}.FMTK")
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ===== CHARGER LES JOUEURS =====
def load_players():
    """Charge tous les joueurs depuis le fichier JSON"""
    try:
        with open('data/players/all_players_complete.json', 'r', encoding='utf-8') as f:
            players = json.load(f)
            print(f"✅ {len(players)} clubs chargés")
            total = sum(len(p) for p in players.values())
            print(f"✅ {total} joueurs chargés")
            return players
    except Exception as e:
        print(f"❌ Erreur chargement joueurs: {e}")
        return {}

PLAYERS_DATA = load_players()

@app.route('/api/players/<club>')
def get_club_players(club):
    """Récupère les joueurs d'un club"""
    if club in PLAYERS_DATA:
        return jsonify({'success': True, 'players': PLAYERS_DATA[club]})
    return jsonify({'success': False, 'message': 'Club non trouvé'}), 404

@app.route('/api/players/search')
def search_players():
    """Recherche des joueurs"""
    query = request.args.get('q', '').lower()
    results = []
    for club, joueurs in PLAYERS_DATA.items():
        for joueur in joueurs:
            if query in joueur.get('nom', '').lower():
                results.append({
                    'nom': joueur['nom'],
                    'club': club,
                    'note': joueur.get('note', 0),
                    'poste': joueur.get('poste', ''),
                    'age': joueur.get('age', 0)
                })
    return jsonify({'success': True, 'results': results[:50]})
