from flask import Flask, send_file, send_from_directory, redirect, request, jsonify
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='.')
app.secret_key = 'dev-secret-key'

# ===== DOSSIER DATA =====
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

@app.route('/accueil/<path:path>')
def accueil_files(path):
    return send_from_directory('accueil', path)

@app.route('/test/<path:path>')
def test_files(path):
    return send_from_directory('test', path)

@app.route('/test/terrain/<path:path>')
def terrain_files(path):
    return send_from_directory('test/terrain', path)

# ===== API : INSCRIPTION =====
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

        # Vérifier si le pseudo existe déjà
        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Ce pseudo existe déjà'}), 400

        # Créer le fichier .FMTK
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
                    'matchs': 0,
                    'victoires': 0,
                    'defaites': 0,
                    'nuls': 0,
                    'buts_marques': 0,
                    'buts_encaisses': 0
                },
                'transferts': {
                    'budget': 50000000,
                    'joueurs_achetes': [],
                    'joueurs_vendus': []
                }
            },
            'session': {
                'games_played': 0,
                'win_rate': 0
            }
        }

        # Sauvegarder
        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)

        return jsonify({
            'success': True,
            'message': 'Inscription réussie !',
            'player': player_data,
            'download': f"/api/download/{pseudo}"
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

# ===== API : CONNEXION =====
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

        # Mettre à jour la date de connexion
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

# ===== API : TÉLÉCHARGER .FMTK =====
@app.route('/api/download/<pseudo>', methods=['GET'])
def download_fmtk(pseudo):
    filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    return send_file(filepath, as_attachment=True, download_name=f"{pseudo}.FMTK")

# ===== API : SAUVEGARDER =====
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

# ===== API : CHARGER SESSION (upload) =====
@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Aucun fichier'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Fichier vide'}), 400

        if not file.filename.endswith('.FMTK'):
            return jsonify({'success': False, 'message': 'Format invalide'}), 400

        content = json.loads(file.read())
        if not content.get('pseudo'):
            return jsonify({'success': False, 'message': 'Fichier invalide'}), 400

        # Sauvegarder sur le serveur
        filepath = os.path.join(DATA_DIR, file.filename)
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)

        return jsonify({
            'success': True,
            'message': 'Fichier chargé avec succès !',
            'data': content
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== FALLBACK =====
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ===== API : SUPPRIMER COMPTE =====
@app.route('/api/delete', methods=['POST'])
def delete_account():
    try:
        data = request.json
        pseudo = data.get('pseudo')
        password = data.get('password')

        filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Compte non trouvé'}), 404

        # Lire le fichier pour vérifier le mot de passe
        with open(filepath, 'r') as f:
            player_data = json.load(f)

        # Ici on vérifie le mot de passe (stocké en clair pour l'instant)
        # Dans une version finale, il faudra le hasher
        # Pour l'instant, on vérifie simplement que le champ existe
        if not password:
            return jsonify({'success': False, 'message': 'Mot de passe requis'}), 400

        # Supprimer le fichier
        os.remove(filepath)

        return jsonify({'success': True, 'message': 'Compte supprimé avec succès'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== ROUTE : TÉLÉCHARGER .FMTK AVEC EXPLORATEUR =====
@app.route('/download/<pseudo>')
def download_fmtk_direct(pseudo):
    filepath = os.path.join(DATA_DIR, f"{pseudo}.FMTK")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    
    # Force le téléchargement avec l'explorateur
    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"{pseudo}.FMTK",
        mimetype='application/json'
    )

# ===== ROUTE : TÉLÉCHARGER .FMTK =====
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

# ===== ROUTE : TÉLÉCHARGER .FMTK =====
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
