class Domain:
    """
    Représente un domaine Active Directory.
    """
    def __init__(self, id, fqdn) :
        self.id = id
        self.fqdn = fqdn
        self.parent_domain = None
        self._forest = None
        self._users = []
        self._servers = []
        
    def get_users(self) :
        return self._users.copy()

    def get_servers(self):
        return self._servers.copy()
    