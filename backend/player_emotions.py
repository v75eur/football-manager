import random

class PlayerEmotions:
    def __init__(self):
        self.emotions = [
            "😊 Heureux", "😤 Frustré", "😎 Confiant", "😰 Stressé", 
            "🤩 Excité", "😔 Déçu", "😡 En colère", "😇 Motivé",
            "🤔 Réfléchi", "😴 Fatigué", "💪 Déterminé", "😟 Inquiet",
            "😁 Enthousiaste", "😒 Boudeur", "😌 Serein", "😳 Surpris"
        ]
        
        self.personnalites = [
            {"type": "Leader", "bonus": 5, "malus": 0, "description": "Motiver les autres"},
            {"type": "Talentueux", "bonus": 8, "malus": -3, "description": "Techniquement doué mais capricieux"},
            {"type": "Travailleur", "bonus": 4, "malus": 0, "description": "Toujours à l'entraînement"},
            {"type": "Fragile", "bonus": 2, "malus": -5, "description": "Mentalement vulnérable"},
            {"type": "Compétiteur", "bonus": 6, "malus": -2, "description": "Veut toujours gagner"},
            {"type": "Esprit d'équipe", "bonus": 3, "malus": 0, "description": "Joue pour le collectif"},
            {"type": "Star", "bonus": 7, "malus": -4, "description": "Attire les projecteurs"},
            {"type": "Rustique", "bonus": 4, "malus": -1, "description": "Fonceur, peu technique"}
        ]
    
    def generer_emotions(self, joueur):
        """Génère l'émotion du joueur selon son état"""
        note = joueur.get('note', 65)
        forme = joueur.get('forme', 70)
        moral = joueur.get('moral', 70)
        
        # Calculer l'état général
        etat = (note + forme + moral) / 3
        
        if etat > 85:
            emotion = random.choice(["😊 Heureux", "😎 Confiant", "🤩 Excité", "😁 Enthousiaste", "💪 Déterminé"])
        elif etat > 70:
            emotion = random.choice(["😇 Motivé", "😌 Serein", "💪 Déterminé", "😁 Enthousiaste"])
        elif etat > 55:
            emotion = random.choice(["🤔 Réfléchi", "😠 En colère", "😟 Inquiet", "😒 Boudeur"])
        else:
            emotion = random.choice(["😤 Frustré", "😰 Stressé", "😔 Déçu", "😡 En colère", "😴 Fatigué"])
        
        return emotion
    
    def generer_personnalite(self):
        """Génère une personnalité aléatoire pour un joueur"""
        return random.choice(self.personnalites)
    
    def impact_emotion_sur_performance(self, joueur):
        """Calcule l'impact de l'émotion sur la performance"""
        emotion = self.generer_emotions(joueur)
        base_perf = joueur.get('note', 65)
        
        # Bonus/Malus selon l'émotion
        bonus_map = {
            "😊 Heureux": 3, "😎 Confiant": 5, "🤩 Excité": 4,
            "😇 Motivé": 3, "💪 Déterminé": 4, "😁 Enthousiaste": 3,
            "😌 Serein": 2, "🤔 Réfléchi": 1,
            "😤 Frustré": -3, "😰 Stressé": -4, "😔 Déçu": -5,
            "😡 En colère": -6, "😴 Fatigué": -4, "😟 Inquiet": -3,
            "😒 Boudeur": -2
        }
        
        bonus = bonus_map.get(emotion, 0)
        
        # Personnalité bonus
        perso = self.generer_personnalite()
        bonus += perso['bonus'] * random.uniform(0.5, 1.5)
        
        performance = min(99, max(40, base_perf + bonus))
        
        return {
            'emotion': emotion,
            'personnalite': perso['type'],
            'performance': round(performance, 1),
            'bonus_total': round(bonus, 1)
        }
    
    def generer_emotions_equipe(self, joueurs):
        """Génère les émotions de toute l'équipe"""
        resultats = []
        for joueur in joueurs:
            resultats.append(self.impact_emotion_sur_performance(joueur))
        return resultats
