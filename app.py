from flask import Flask, send_file, send_from_directory, redirect, request, jsonify
import os
import json
import uuid
import hmac
import hashlib
import base64
from datetime import datetime
from cryptography.fernet import Fernet

app = Flask(__name__, static_folder='.')
app.secret_key = 'dev-secret-key-change-in-production'

# ===== DOSSIER DATA =====
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# ===== CLÉ SECRÈTE POUR LES SIGNATURES =====
SECRET_KEY = app.secret_key.encode()
SALT = b'fmtk_salt_2026'

# ===== GÉNÉRER UNE CLÉ FERNET (chiffrement) =====
try:
    with open('data/.fernet_key', 'rb') as f:
        FERNET_KEY = f.read()
except:
    FERNET_KEY = Fernet.generate_key()
    with open('data/.fernet_key', 'wb') as f:
        f.write(FERNET_KEY)

cipher = Fernet(FERNET_KEY)

# ============================================
# FONCTIONS DE SÉCURISATION
# ============================================
def generate_signature(data):
    """Génère une signature HMAC pour le fichier"""
    json_str = json.dumps(data, sort_keys=True)
    signature = hmac.new(SECRET_KEY, json_str.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def verify_signature(data, signature):
    """Vérifie la signature du fichier"""
    json_str = json.dumps(data, sort_keys=True)
    expected = hmac.new(SECRET_KEY, json_str.encode(), hashlib.sha256).digest()
    expected_b64 = base64.b64encode(expected).decode()
    return hmac.compare_digest(signature, expected_b64)

def encrypt_player_data(player_data):
    """Chiffre les données sensibles"""
    json_str = json.dumps(player_data)
    encrypted = cipher.encrypt(json_str.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_player_data(encrypted_data):
    """Déchiffre les données"""
    decrypted = cipher.decrypt(base64.b64decode(encrypted_data))
    return json.loads(decrypted.decode())

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
# API : LISTE DES JOUEURS (admin)
# ============================================
@app.route('/api/players', methods=['GET'])
def list_players():
    try:
        files = os.listdir(DATA_DIR)
        players = []
        for f in files:
            if f.endswith('.FMTK'):
                players.append(f.replace('.FMTK', ''))
        return jsonify({'players': players})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# API : INSCRIPTION AVEC SIGNATURE
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

        # Vérifier email/WhatsApp uniques
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.FMTK'):
                try:
                    with open(os.path.join(DATA_DIR, filename), 'r') as f:
                        existing = json.load(f)
                        if existing.get('email') == email:
                            return jsonify({'success': False, 'message': 'Cet email est déjà utilisé'}), 400
                        if existing.get('whatsapp') == whatsapp and whatsapp:
                            return jsonify({'success': False, 'message': 'Ce numéro WhatsApp est déjà utilisé'}), 400
                except:
                    pass

        # Créer les données du joueur
        player_data = {
            'version': '2.0',
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

        # ===== GÉNÉRER LA SIGNATURE =====
        signature = generate_signature(player_data)

        # ===== FICHIER CHIFFRÉ + SIGNATURE =====
        encrypted_data = encrypt_player_data(player_data)

        # Sauvegarder le fichier avec signature
        file_content = {
            'data': encrypted_data,
            'signature': signature,
            'version': '2.0',
            'player_id': player_data['player_id']
        }

        with open(filepath, 'w') as f:
            json.dump(file_content, f, indent=2)

        return jsonify({
            'success': True,
            'message': 'Inscription réussie !',
            'player': player_data,
            'signature': signature
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ============================================
# API : CONNEXION AVEC VÉRIFICATION
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
            file_content = json.load(f)

        # ===== VÉRIFIER LA SIGNATURE =====
        encrypted_data = file_content.get('data')
        signature = file_content.get('signature')

        if not encrypted_data or not signature:
            return jsonify({'success': False, 'message': 'Fichier corrompu'}), 400

        # Déchiffrer
        try:
            player_data = decrypt_player_data(encrypted_data)
        except:
            return jsonify({'success': False, 'message': 'Fichier invalide'}), 400

        # Vérifier la signature
        if not verify_signature(player_data, signature):
            return jsonify({'success': False, 'message': 'Signature invalide - Fichier modifié'}), 400

        # Mettre à jour la dernière connexion
        player_data['last_login'] = datetime.now().isoformat()

        # Regénérer la signature
        new_signature = generate_signature(player_data)
        new_encrypted = encrypt_player_data(player_data)

        file_content['data'] = new_encrypted
        file_content['signature'] = new_signature

        with open(filepath, 'w') as f:
            json.dump(file_content, f, indent=2)

        return jsonify({
            'success': True,
            'message': f'Bienvenue {pseudo} !',
            'player': player_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ============================================
# API : SAUVEGARDER AVEC SIGNATURE
# ============================================
@app.route('/api/save', methods=['POST'])
def save():
    try:
        data = request.json
        pseudo = data.get('pseudo')
        player_data = data.get('data')

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Fichier non trouvé'}), 404

        # ===== VÉRIFIER L'EXISTANT =====
        with open(filepath, 'r') as f:
            file_content = json.load(f)

        # ===== CRÉER NOUVELLE SIGNATURE =====
        signature = generate_signature(player_data)
        encrypted_data = encrypt_player_data(player_data)

        file_content['data'] = encrypted_data
        file_content['signature'] = signature

        with open(filepath, 'w') as f:
            json.dump(file_content, f, indent=2)

        return jsonify({'success': True, 'message': 'Sauvegarde effectuée !'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# ROUTE : TÉLÉCHARGER .FMTK (format sécurisé)
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
# API : VÉRIFIER UN FICHIER .FMTK (upload)
# ============================================
@app.route('/api/verify', methods=['POST'])
def verify_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Aucun fichier'}), 400

        file = request.files['file']
        content = json.load(file)

        # Vérifier la signature
        encrypted_data = content.get('data')
        signature = content.get('signature')

        if not encrypted_data or not signature:
            return jsonify({'success': False, 'message': 'Fichier invalide - Pas de signature'}), 400

        try:
            player_data = decrypt_player_data(encrypted_data)
        except:
            return jsonify({'success': False, 'message': 'Fichier corrompu'}), 400

        if not verify_signature(player_data, signature):
            return jsonify({'success': False, 'message': '❌ Fichier modifié ! Signature invalide'}), 400

        return jsonify({
            'success': True,
            'message': '✅ Fichier valide !',
            'player': player_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
