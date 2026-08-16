from flask import Flask, send_file, send_from_directory
import os

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_file('acceuil/acceuil.html')

@app.route('/acceuil/<path:path>')
def acceuil_files(path):
    return send_from_directory('acceuil', path)

# Route pour les autres fichiers HTML que tu ajouteras
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_file(path)
    return "Fichier non trouvé", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

@app.route('/session/charger')
def session_charger():
    return send_file('session/charger.html')
