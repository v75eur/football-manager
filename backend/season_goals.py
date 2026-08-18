import random

class SeasonGoals:
    def __init__(self):
        self.objectifs = []
        self.recompenses = []
    
    def generer_objectifs(self, club_niveau):
        """Génère des objectifs pour la saison"""
        objectifs = []
        
        # Objectifs selon le niveau du club
        if club_niveau >= 4:  # Grand club
            objectifs = [
                {"nom": "🏆 Gagner le championnat", "recompense": 15, "status": "en_cours"},
                {"nom": "🌍 Qualification Ligue des Champions", "recompense": 10, "status": "en_cours"},
                {"nom": "🏅 Atteindre les quarts de finale de C1", "recompense": 8, "status": "en_cours"},
                {"nom": "⚽ Meilleur buteur du championnat", "recompense": 5, "status": "en_cours"}
            ]
        elif club_niveau >= 2:  # Club moyen
            objectifs = [
                {"nom": "🏆 Top 5 du championnat", "recompense": 10, "status": "en_cours"},
                {"nom": "🏆 Victoire en coupe nationale", "recompense": 8, "status": "en_cours"},
                {"nom": "📈 Progression de 3 places au classement", "recompense": 5, "status": "en_cours"},
                {"nom": "💪 Finir avec un budget positif", "recompense": 4, "status": "en_cours"}
            ]
        else:  # Petit club
            objectifs = [
                {"nom": "🛡️ Éviter la relégation", "recompense": 8, "status": "en_cours"},
                {"nom": "🏆 Atteindre les 40 points", "recompense": 6, "status": "en_cours"},
                {"nom": "⭐ Révélation de la saison", "recompense": 4, "status": "en_cours"},
                {"nom": "📈 Meilleure défense de la saison", "recompense": 3, "status": "en_cours"}
            ]
        
        self.objectifs = objectifs
        return objectifs
    
    def verifier_objectifs(self, classement, stats_equipe):
        """Vérifie si les objectifs sont atteints"""
        for obj in self.objectifs:
            if obj['status'] != 'en_cours':
                continue
            
            # Vérifier selon l'objectif
            if obj['nom'].startswith("🏆 Gagner le championnat"):
                if classement[0][0] == stats_equipe['nom']:
                    obj['status'] = 'complet'
                    self.recompenses.append(obj['recompense'])
            
            elif obj['nom'].startswith("🏆 Top 5"):
                pos = [i for i, e in enumerate(classement) if e[0] == stats_equipe['nom']]
                if pos and pos[0] + 1 <= 5:
                    obj['status'] = 'complet'
                    self.recompenses.append(obj['recompense'])
            
            elif obj['nom'].startswith("🛡️ Éviter la relégation"):
                pos = [i for i, e in enumerate(classement) if e[0] == stats_equipe['nom']]
                if pos and pos[0] + 1 <= len(classement) - 3:
                    obj['status'] = 'complet'
                    self.recompenses.append(obj['recompense'])
    
    def get_recompenses(self):
        """Retourne les récompenses obtenues"""
        return sum(self.recompenses)
