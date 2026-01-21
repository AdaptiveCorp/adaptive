# src/lab_ad/models/forest.py

"""
Module contenant la classe Forest pour la gestion des forêts AD.
"""

class Forest:
    """Représente une forêt Active Directory."""
    
    def __init__(self, id, fqdn):
        self.id = id
        self.fqdn = fqdn
        self._domains = []
    
    def add_domain(self, domain):
        if domain not in self._domains:
            self._domains.append(domain)
    
    def get_all_domains(self):
        return self._domains.copy()
