import random

class TeamComposition:
    def __init__(self):
        self.formation = "4-3-3"
        self.titulaires = []
        self.remplacants = []
        self.entraineur = {
            'nom': 'Coach',
            'experience': 5,
            'style': 'Attaque'
        }
    
    def choisir_titulaires(self, joueurs, formation="4-3-3"):
        """Choisit les 11 titulaires selon la formation"""
        self.formation = formation
        postes_necessaires = {
            "4-3-3": {"Gardien": 1, "Défenseur": 4, "Milieu": 3, "Attaquant": 3},
            "4-4-2": {"Gardien": 1, "Défenseur": 4, "Milieu": 4, "Attaquant": 2},
            "3-5-2": {"Gardien": 1, "Défenseur": 3, "Milieu": 5, "Attaquant": 2},
            "5-3-2": {"Gardien": 1, "Défenseur": 5, "Milieu": 3, "Attaquant": 2},
            "4-2-3-1": {"Gardien": 1, "Défenseur": 4, "Milieu": 5, "Attaquant": 1}
        }
        
        besoins = postes_necessaires.get(formation, postes_necessaires["4-3-3"])
        titulaires = []
        remplacants = []
        
        # Classer les joueurs par poste
        joueurs_par_poste = {}
        for joueur in joueurs:
            poste = joueur.get('poste', 'Milieu')
            if poste not in joueurs_par_poste:
                joueurs_par_poste[poste] = []
            joueurs_par_poste[poste].append(joueur)
        
        # Trier par note
        for poste in joueurs_par_poste:
            joueurs_par_poste[poste].sort(key=lambda x: x.get('note', 60), reverse=True)
        
        # Choisir les titulaires
        for poste, nb in besoins.items():
            if poste in joueurs_par_poste:
                disponibles = joueurs_par_poste[poste]
                for _ in range(min(nb, len(disponibles))):
                    if disponibles:
                        titulaires.append(disponibles.pop(0))
        
        # Les autres joueurs vont sur le banc
        for poste, joueurs_list in joueurs_par_poste.items():
            remplacants.extend(joueurs_list)
        
        self.titulaires = titulaires
        self.remplacants = remplacants
        
        return {
            'titulaires': titulaires,
            'remplacants': remplacants
        }
    
    def effectuer_remplacement(self, joueur_sortant, joueur_entrant):
        """Effectue un remplacement pendant le match"""
        if joueur_sortant in self.titulaires and joueur_entrant in self.remplacants:
            idx = self.titulaires.index(joueur_sortant)
            self.titulaires[idx] = joueur_entrant
            self.remplacants[self.remplacants.index(joueur_entrant)] = joueur_sortant
            return True
        return False
    
    def calculer_note_equipe(self):
        """Calcule la note moyenne de l'équipe"""
        if not self.titulaires:
            return 65
        notes = [j.get('note', 60) for j in self.titulaires]
        return round(sum(notes) / len(notes), 1)
