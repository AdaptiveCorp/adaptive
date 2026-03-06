
"""
Module contenant la classe principale LabProject.
"""

from .models import Forest, Domain, User

class LabProject:
    """Point d'entrée principal du lab."""
    
    def __init__(self, id, name, created_at):
        self.id = id
        self.name = name
        self.created_at = created_at
        
        # Lien avec d'autres classe
        self._forests = {}
        self._domains = {}
    
    def create_forest(self, forest_id, fqdn):
        forest = Forest(forest_id, self.id, fqdn)
        self._forests[forest_id] = forest
        return forest

    def compute(self):
        """
        Méthode qui appelle le moteur de déploiement pour déployer le projet sur l'hyperviseur
        
        :param self: Description
        """
        return None

    def validate(self):
        """
        Fonction qui permet de vérifier la cohérence du projet
        
        :param self: Description
        """
        return None