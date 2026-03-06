class Server:
    """Représente un serveur Active Directory."""
    
    def __init__(self, id, fqdn) :
        self.id = id
        self.domain_id = None
        self.forest_id = None
        self.fqdn = fqdn
        self.is_dc = False
        self.ip = None
        self.gtw = None
        self.dns = None
        

    def get_users(self) :
        return self._users.copy()

    def get_servers(self):
        return self._servers.copy()
    