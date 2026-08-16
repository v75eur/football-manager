from flask import Flask, send_file, send_from_directory
import os

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_file('accueil/index.html')

@app.route('/accueil/<path:path>')
def accueil_files(path):
    return send_from_directory('accueil', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
