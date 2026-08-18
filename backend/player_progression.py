import json
import random
from datetime import datetime, timedelta

class PlayerProgression:
    def __init__(self):
        self.growth_factors = {
            "Gardien": {"reflexes": 0.8, "placement": 0.7, "plongeon": 0.6},
            "Défenseur": {"tacle": 0.8, "interception": 0.7, "marquage": 0.7},
            "Milieu": {"passe": 0.9, "vision": 0.8, "technique": 0.7},
            "Attaquant": {"finition": 0.8, "tir": 0.8, "vitesse": 0.7}
        }
    
    def progresser_joueur(self, joueur, match_played, performance):
        """Fait évoluer un joueur après un match"""
        # Facteurs de progression
        age = joueur.get('age', 25)
        note = joueur.get('note', 70)
        
        # Les jeunes progressent plus vite
        if age < 22:
            progression_base = random.uniform(1.5, 3.0)
        elif age < 27:
            progression_base = random.uniform(0.8, 1.8)
        elif age < 32:
            progression_base = random.uniform(0.3, 0.8)
        else:
            progression_base = random.uniform(-0.5, 0.3)  # Déclin
        
        # Performance influence la progression
        if performance > 80:
            progression_base *= 1.5
        elif performance < 60:
            progression_base *= 0.5
        
        # Mettre à jour la note
        nouvelle_note = min(99, note + progression_base)
        joueur['note'] = round(nouvelle_note, 1)
        
        # Mettre à jour les attributs secondaires
        for attr in ['vitesse', 'tir', 'passe', 'dribble']:
            if attr in joueur:
                variation = random.uniform(-0.5, 0.8)
                joueur[attr] = min(99, max(40, joueur[attr] + variation))
        
        return joueur
    
    def generer_jeune_talent(self, pays, club):
        """Génère un jeune joueur talentueux (15-17 ans)"""
        postes = ["Gardien", "Défenseur Central", "Latéral", "Milieu Défensif", 
                  "Milieu Central", "Milieu Offensif", "Ailier", "Attaquant"]
        
        poste = random.choice(postes)
        age = random.randint(15, 17)
        note = random.randint(60, 80)  # Talent précoce
        
        joueur = {
            "nom": f"Jeune Talent {random.randint(1, 100)}",
            "age": age,
            "poste": poste,
            "pays": pays,
            "club": club,
            "note": note,
            "vitesse": random.randint(60, 85),
            "tir": random.randint(50, 75),
            "passe": random.randint(55, 80),
            "dribble": random.randint(55, 80),
            "potentiel": random.randint(80, 95)  # Potentiel élevé
        }
        return joueur
    
    def mettre_a_jour_effectif(self, players_data):
        """Met à jour tous les joueurs en fin de saison"""
        for club, joueurs in players_data.items():
            for joueur in joueurs:
                # Progression naturelle
                if random.random() < 0.3:  # 30% de chance de progresser
                    joueur = self.progresser_joueur(joueur, True, random.randint(40, 85))
                
                # Ajouter un jeune talent si nécessaire
                if random.random() < 0.05 and len(joueurs) < 30:  # 5% de chance
                    jeune = self.generer_jeune_talent(joueur.get('pays', 'France'), club)
                    joueurs.append(jeune)
        
        return players_data
