from collections import defaultdict
from ..database import orm_models
from sqlalchemy.orm import Session



def get_dcs_grouped_by_domain(project_id: int, db: Session):
    """
    Récupère les DCs groupés par domaine
    
    :param project_id: ID du projet
    :param db: Session DB
    :return: Liste de listes [[DC1_DOM1, DC2_DOM1], [DC1_DOM2, DC2_DOM2]]
    """

    dc_servers = db.query(orm_models.DBServer).filter(
        orm_models.DBServer.project_id == project_id,
        orm_models.DBServer.is_dc == True
    ).order_by(orm_models.DBServer.domain_id, orm_models.DBServer.id).all()
    
    domains_dict = defaultdict(list)
    for dc in dc_servers:
        domains_dict[dc.domain_id].append(dc)
    
    results = list(domains_dict.values())
    
    return results

def get_domain(domain_id: int, db: Session):
    """
    Récupère le Domain par rapport à son ID
    
    :param domain_id: ID du domain
    :param db: Session DB
    :return: DBDomain 
    """

    domain = db.query(orm_models.DBDomain).filter(
        orm_models.DBDomain.id == domain_id,
    ).first()
    
    return domain
