class User:
    """Représente un utilisateur Active Directory."""
    
    def __init__(self, id, fqdn):
        self.id = id
        self.fqdn = fqdn
        self._forest = None
        self._users = []
        self._servers = []




    