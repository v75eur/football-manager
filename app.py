from flask import Flask, send_file, send_from_directory, redirect, request, jsonify
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='.')
app.secret_key = 'dev-secret-key'

# ===== DOSSIER DATA (SAUVEGARDE) =====
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================
# ROUTES PRINCIPALES
# ============================================
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

@app.route('/accueil/<path:path>')
def accueil_files(path):
    return send_from_directory('accueil', path)

@app.route('/test/<path:path>')
def test_files(path):
    return send_from_directory('test', path)

@app.route('/test/terrain/<path:path>')
def terrain_files(path):
    return send_from_directory('test/terrain', path)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'OK', 'message': 'Le serveur fonctionne !'})

# ============================================
# API : LISTE DES JOUEURS
# ============================================
@app.route('/api/players', methods=['GET'])
def list_players():
    try:
        files = os.listdir(DATA_DIR)
        players = [f.replace('.FMTK', '') for f in files if f.endswith('.FMTK')]
        return jsonify({'players': players})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# API : INSCRIPTION (avec sauvegarde forcée)
# ============================================
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

        player_data = {
            'version': '1.0',
            'pseudo': pseudo,
            'email': email,
            'whatsapp': whatsapp,
            'country': country,
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'player_id': str(uuid.uuid4()),
            'equipe': {
                'nom': '',
                'division': '',
                'pays': '',
                'stade': '',
                'couleurs': '#FFD700 / #003366',
                'terrain': 'style1_classique.html',
                'joueurs': [],
                'stats': {
                    'matchs': 0, 'victoires': 0, 'defaites': 0, 'nuls': 0,
                    'buts_marques': 0, 'buts_encaisses': 0
                },
                'transferts': {'budget': 50000000, 'joueurs_achetes': [], 'joueurs_vendus': []},
                'tactique': {'formation': '4-3-3', 'style': 'Attaque'}
            },
            'session': {'games_played': 0, 'win_rate': 0}
        }

        # ===== SAUVEGARDE OBLIGATOIRE =====
        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)

        if not os.path.exists(filepath):
            raise Exception("Le fichier n'a pas pu être créé")

        return jsonify({
            'success': True,
            'message': 'Inscription réussie !',
            'player': player_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ============================================
# API : CONNEXION
# ============================================
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        pseudo = data.get('pseudo', '').strip()
        password = data.get('password', '').strip()

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Joueur non trouvé'}), 404

        with open(filepath, 'r') as f:
            player_data = json.load(f)

        player_data['last_login'] = datetime.now().isoformat()
        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)

        return jsonify({
            'success': True,
            'message': f'Bienvenue {pseudo} !',
            'player': player_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ============================================
# API : SAUVEGARDER
# ============================================
@app.route('/api/save', methods=['POST'])
def save():
    try:
        data = request.json
        pseudo = data.get('pseudo')
        player_data = data.get('data')

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)

        return jsonify({'success': True, 'message': 'Sauvegarde effectuée !'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# ROUTE : TÉLÉCHARGER .FMTK
# ============================================
@app.route('/download/<pseudo>')
def download_fmtk(pseudo):
    filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"{pseudo}.FMTK",
        mimetype='application/json'
    )

# ============================================
# API : GENERER DES JOUEURS
# ============================================
@app.route('/api/generate_players', methods=['POST'])
def generate_players():
    try:
        import random
        data = request.json
        pays = data.get('pays', 'France')
        club = data.get('club', 'Mon Club')
        nombre = data.get('nombre', 25)
        
        with open('data/all_players_complete_200k.json', 'r') as f:
            all_players = json.load(f)
        
        players_from_country = [p for p in all_players if p.get('pays') == pays]
        if len(players_from_country) < nombre:
            players_from_country = all_players
        
        selected = random.sample(players_from_country, min(nombre, len(players_from_country)))
        for p in selected:
            p['club'] = club
        
        return jsonify({'success': True, 'players': selected})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# FALLBACK
# ============================================
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_file(path)
    elif os.path.exists(f'test/terrain/{path}'):
        return send_from_directory('test/terrain', path)
    elif os.path.exists(f'test/{path}'):
        return send_from_directory('test', path)
    else:
        return redirect('/')

# ============================================
# LANCEMENT
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
