import json
import random
from datetime import datetime, timedelta

class CompetitionManager:
    def __init__(self):
        self.saison = 1
        self.journee = 1
        
    def generer_calendrier(self, equipes, nbr_equipes=20):
        """Génère un calendrier aller-retour"""
        calendrier = []
        
        # S'assurer que toutes les équipes sont uniques
        equipes_uniques = list(set(equipes))
        if len(equipes_uniques) < nbr_equipes:
            # Ajouter des équipes fictives si besoin
            for i in range(nbr_equipes - len(equipes_uniques)):
                equipes_uniques.append(f"Équipe {i+1}")
        
        equipes_uniques = equipes_uniques[:nbr_equipes]
        
        # Calendrier aller
        for i in range(len(equipes_uniques)):
            for j in range(i+1, len(equipes_uniques)):
                calendrier.append({
                    'journee': len(calendrier) // (len(equipes_uniques)//2) + 1,
                    'equipe1': equipes_uniques[i],
                    'equipe2': equipes_uniques[j],
                    'aller': True,
                    'score1': None,
                    'score2': None,
                    'joué': False
                })
        
        # Calendrier retour
        for match in calendrier.copy():
            if match['aller']:
                calendrier.append({
                    'journee': len(calendrier) // (len(equipes_uniques)//2) + 1,
                    'equipe1': match['equipe2'],
                    'equipe2': match['equipe1'],
                    'aller': False,
                    'score1': None,
                    'score2': None,
                    'joué': False
                })
        
        return calendrier
    
    def simuler_match_championnat(self, equipe1, equipe2, force1=70, force2=70):
        """Simule un match de championnat"""
        # Force des équipes
        f1 = force1 + random.uniform(-10, 10)
        f2 = force2 + random.uniform(-10, 10)
        
        # Avantage domicile
        f1 *= 1.05
        
        # Buts
        buts1 = max(0, round(random.poisson(f1 / 12) + random.uniform(-0.5, 0.5)))
        buts2 = max(0, round(random.poisson(f2 / 12) + random.uniform(-0.5, 0.5)))
        
        # Statistiques
        possession1 = random.randint(40, 60)
        possession2 = 100 - possession1
        tirs1 = random.randint(5, 20)
        tirs2 = random.randint(5, 20)
        fautes = random.randint(5, 15)
        jaunes = random.randint(0, 4)
        rouges = random.randint(0, 1)
        
        return {
            'score1': buts1,
            'score2': buts2,
            'possession1': possession1,
            'possession2': possession2,
            'tirs1': tirs1,
            'tirs2': tirs2,
            'fautes': fautes,
            'cartons_jaunes': jaunes,
            'cartons_rouges': rouges,
            'vainqueur': 'equipe1' if buts1 > buts2 else 'equipe2' if buts2 > buts1 else 'nul'
        }
    
    def classement(self, equipes, matchs):
        """Calcule le classement"""
        classement = {}
        
        # Initialiser
        for equipe in equipes:
            classement[equipe] = {
                'joues': 0,
                'victoires': 0,
                'nuls': 0,
                'defaites': 0,
                'buts_marques': 0,
                'buts_encaisses': 0,
                'points': 0
            }
        
        # Appliquer les résultats
        for match in matchs:
            if match['joué'] and match['score1'] is not None:
                e1 = match['equipe1']
                e2 = match['equipe2']
                s1 = match['score1']
                s2 = match['score2']
                
                classement[e1]['joues'] += 1
                classement[e2]['joues'] += 1
                classement[e1]['buts_marques'] += s1
                classement[e1]['buts_encaisses'] += s2
                classement[e2]['buts_marques'] += s2
                classement[e2]['buts_encaisses'] += s1
                
                if s1 > s2:
                    classement[e1]['victoires'] += 1
                    classement[e1]['points'] += 3
                    classement[e2]['defaites'] += 1
                elif s2 > s1:
                    classement[e2]['victoires'] += 1
                    classement[e2]['points'] += 3
                    classement[e1]['defaites'] += 1
                else:
                    classement[e1]['nuls'] += 1
                    classement[e2]['nuls'] += 1
                    classement[e1]['points'] += 1
                    classement[e2]['points'] += 1
        
        # Trier
        classement_trie = sorted(
            classement.items(),
            key=lambda x: (-x[1]['points'], -x[1]['victoires'], (x[1]['buts_marques'] - x[1]['buts_encaisses']))
        )
        
        return classement_trie
