from flask import Flask, send_file, send_from_directory, request, jsonify
import os
import json
import uuid
import hashlib
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
app.secret_key = 'dev-secret-key-change-in-production'
CORS(app)

# ===== DOSSIER DATA =====
# Utiliser le chemin absolu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

print(f"📁 DATA_DIR: {DATA_DIR}")
print(f"📁 Contenu: {os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else 'vide'}")

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
        print(f"📥 Register: {data}")
        
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
        print(f"📁 Chemin: {filepath}")
        
        if os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Ce pseudo existe déjà'}), 400

        # Vérifier email unique
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.FMTK'):
                try:
                    with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                        if existing.get('email') == email:
                            return jsonify({'success': False, 'message': 'Cet email est déjà utilisé'}), 400
                        if existing.get('whatsapp') == whatsapp and whatsapp:
                            return jsonify({'success': False, 'message': 'Ce numéro WhatsApp est déjà utilisé'}), 400
                except Exception as e:
                    print(f"⚠️ Erreur lecture {filename}: {e}")

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
                'stats': {
                    'matchs': 0, 'victoires': 0, 'defaites': 0,
                    'nuls': 0, 'buts_marques': 0, 'buts_encaisses': 0
                },
                'transferts': {
                    'budget': 50000000,
                    'joueurs_achetes': [],
                    'joueurs_vendus': []
                },
                'tactique': {
                    'formation': '4-3-3'
                }
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fichier créé: {filepath}")

        return jsonify({
            'success': True,
            'message': 'Inscription réussie !',
            'pseudo': pseudo,
            'player_id': player_data['player_id']
        })

    except Exception as e:
        print(f"❌ Erreur register: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ===== API LOGIN =====
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        print(f"📥 Login: {data}")
        
        pseudo = data.get('pseudo', '').strip()
        password = data.get('password', '').strip()

        if not pseudo or not password:
            return jsonify({'success': False, 'message': 'Pseudo et mot de passe requis'}), 400

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        print(f"📁 Login chemin: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"❌ Fichier non trouvé: {filepath}")
            # Lister les fichiers disponibles
            print(f"📁 Fichiers disponibles: {os.listdir(DATA_DIR)}")
            return jsonify({'success': False, 'message': 'Compte inexistant'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            player_data = json.load(f)

        hashed = hashlib.sha256(password.encode()).hexdigest()
        if player_data.get('password') != hashed:
            return jsonify({'success': False, 'message': 'Mot de passe incorrect'}), 401

        player_data['last_login'] = datetime.now().isoformat()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'pseudo': pseudo,
            'player_id': player_data.get('player_id')
        })

    except Exception as e:
        print(f"❌ Erreur login: {e}")
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

# ===== LISTER LES FICHIERS (debug) =====
@app.route('/api/list-files')
def list_files():
    try:
        files = os.listdir(DATA_DIR)
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
