class PlayerStats:
    def __init__(self):
        self.statistiques = {}
    
    def initialiser_stats(self, joueur):
        """Initialise les statistiques d'un joueur"""
        self.statistiques[joueur['nom']] = {
            'buts': 0,
            'passes': 0,
            'cartons_jaunes': 0,
            'cartons_rouges': 0,
            'matchs': 0,
            'minutes': 0,
            'notes': [],
            'tirs': 0,
            'tirs_cadres': 0,
            'interceptions': 0,
            'tacles': 0
        }
        return self.statistiques[joueur['nom']]
    
    def enregistrer_match(self, joueur, stats_match):
        """Enregistre les stats d'un match"""
        nom = joueur['nom']
        if nom not in self.statistiques:
            self.initialiser_stats(joueur)
        
        stat = self.statistiques[nom]
        stat['matchs'] += 1
        stat['buts'] += stats_match.get('buts', 0)
        stat['passes'] += stats_match.get('passes', 0)
        stat['minutes'] += stats_match.get('minutes', 90)
        stat['tirs'] += stats_match.get('tirs', 0)
        stat['tirs_cadres'] += stats_match.get('tirs_cadres', 0)
        stat['interceptions'] += stats_match.get('interceptions', 0)
        stat['tacles'] += stats_match.get('tacles', 0)
        stat['notes'].append(stats_match.get('note', 60))
        
        if stats_match.get('carton_jaune', False):
            stat['cartons_jaunes'] += 1
        if stats_match.get('carton_rouge', False):
            stat['cartons_rouges'] += 1
        
        return stat
    
    def top_buteurs(self, n=5):
        """Retourne les meilleurs buteurs"""
        buteurs = []
        for nom, stat in self.statistiques.items():
            if stat['buts'] > 0:
                buteurs.append({
                    'nom': nom,
                    'buts': stat['buts'],
                    'matchs': stat['matchs'],
                    'ratio': round(stat['buts'] / max(1, stat['matchs']), 2)
                })
        return sorted(buteurs, key=lambda x: x['buts'], reverse=True)[:n]
    
    def top_passeurs(self, n=5):
        """Retourne les meilleurs passeurs"""
        passeurs = []
        for nom, stat in self.statistiques.items():
            if stat['passes'] > 0:
                passeurs.append({
                    'nom': nom,
                    'passes': stat['passes'],
                    'matchs': stat['matchs'],
                    'ratio': round(stat['passes'] / max(1, stat['matchs']), 2)
                })
        return sorted(passeurs, key=lambda x: x['passes'], reverse=True)[:n]
    
    def meilleurs_joueurs(self, n=5):
        """Retourne les meilleurs joueurs (note moyenne)"""
        joueurs = []
        for nom, stat in self.statistiques.items():
            if stat['notes']:
                moyenne = round(sum(stat['notes']) / len(stat['notes']), 1)
                joueurs.append({
                    'nom': nom,
                    'note_moyenne': moyenne,
                    'matchs': stat['matchs']
                })
        return sorted(joueurs, key=lambda x: x['note_moyenne'], reverse=True)[:n]
