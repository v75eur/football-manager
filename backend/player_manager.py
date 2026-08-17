import json
import os
import uuid
from datetime import datetime

class PlayerManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def create_player_file(self, pseudo, email, whatsapp):
        player_data = {
            'version': '1.0',
            'pseudo': pseudo,
            'email': email,
            'whatsapp': whatsapp,
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
                },
                'tactique': {
                    'formation': '4-3-3',
                    'style': 'Attaque'
                }
            },
            'session': {
                'games_played': 0,
                'win_rate': 0
            }
        }
        filepath = f"{self.data_dir}/{pseudo}.FMTK"
        with open(filepath, 'w') as f:
            json.dump(player_data, f, indent=2)
        return player_data
    
    def load_player_file(self, pseudo):
        filepath = f"{self.data_dir}/{pseudo}.FMTK"
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def update_player_file(self, pseudo, data):
        filepath = f"{self.data_dir}/{pseudo}.FMTK"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
