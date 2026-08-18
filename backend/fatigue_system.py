import random

class FatigueSystem:
    def __init__(self):
        self.niveaux = {
            "Reposé": 0,
            "Légère": 20,
            "Modérée": 40,
            "Fatigué": 60,
            "Épuisé": 80
        }
    
    def calculer_fatigue(self, joueur, matchs_joues, intensite_entrainement):
        """Calcule la fatigue d'un joueur"""
        age = joueur.get('age', 25)
        base_fatigue = 0
        
        # Fatigue par match
        if matchs_joues > 0:
            base_fatigue += matchs_joues * 3
        
        # Âge
        if age > 30:
            base_fatigue += (age - 30) * 2
        
        # Entraînement
        if intensite_entrainement > 70:
            base_fatigue += intensite_entrainement / 100 * 10
        
        # Fatigue aléatoire
        base_fatigue += random.randint(-5, 10)
        
        # Niveau de fatigue
        niveau = "Reposé"
        if base_fatigue > 70:
            niveau = "Épuisé"
        elif base_fatigue > 50:
            niveau = "Fatigué"
        elif base_fatigue > 30:
            niveau = "Modérée"
        elif base_fatigue > 10:
            niveau = "Légère"
        
        return {
            'niveau': niveau,
            'valeur': min(100, max(0, base_fatigue)),
            'impact': self.impact_fatigue(base_fatigue)
        }
    
    def impact_fatigue(self, fatigue):
        """Impact de la fatigue sur les performances"""
        if fatigue < 20:
            return 0
        elif fatigue < 40:
            return -2
        elif fatigue < 60:
            return -5
        elif fatigue < 80:
            return -10
        else:
            return -15
    
    def recuperer(self, joueur, jours_repos):
        """Récupération après des jours de repos"""
        fatigue = joueur.get('fatigue', 0)
        reduction = jours_repos * 8
        nouvelle_fatigue = max(0, fatigue - reduction)
        return nouvelle_fatigue
    
    def generer_blessure(self, fatigue, intensite_match):
        """Génère une blessure selon fatigue et intensité"""
        risque = fatigue / 100 * 50 + intensite_match / 10
        
        if risque > 80 and random.random() < 0.1:
            duree = random.randint(1, 4) * 7  # jours
            return {
                'blesse': True,
                'duree': duree,
                'type': random.choice(["Légère", "Modérée", "Grave"]),
                'jours_restants': duree
            }
        return {'blesse': False}
