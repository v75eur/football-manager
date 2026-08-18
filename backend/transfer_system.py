
    def generer_marche(self, joueurs_disponibles, budget_equipe):
        """Génère un marché des transferts"""
        marche = []
        for joueur in joueurs_disponibles[:20]:
            valeur = self.calculer_valeur_joueur(joueur)
            if random.random() < 0.3:  # 30% des joueurs sont sur le marché
                marche.append({
                    'joueur': joueur,
                    'prix': valeur * random.uniform(0.8, 1.2),
                    'club_actuel': joueur.get('club', 'Inconnu'),
                    'interet': random.randint(1, 5)  # Niveau d'intérêt
                })
        return marche
    
    def transfert_automatique(self, equipe, marche, budget):
        """L'IA fait des transferts automatiques"""
        if not marche or budget < 5:
            return None
        
        # Filtrer les joueurs abordables
        abordables = [m for m in marche if m['prix'] < budget * 0.8]
        if not abordables:
            return None
        
        # Choisir un joueur aléatoire
        cible = random.choice(abordables)
        
        # Négociation
        offre = cible['prix'] * random.uniform(0.7, 0.95)
        if offre < budget:
            return {
                'joueur': cible['joueur'],
                'prix': round(offre, 2),
                'success': True,
                'message': f"Le club a recruté {cible['joueur']['nom']} pour {round(offre, 2)} M€"
            }
        
        return None
