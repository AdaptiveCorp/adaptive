from collections import defaultdict

from sqlalchemy.orm import Session

from adaptive.models.domain import Domain
from adaptive.models.server import Server


def get_dcs_grouped_by_domain(db: Session):
    """
    Récupère les DCs groupés par domaine

    :param db: Session DB
    :return: Liste de listes [[DC1_DOM1, DC2_DOM1], [DC1_DOM2, DC2_DOM2]]
    """

    dc_servers = (
        db.query(Server)
        .filter(Server.is_dc)
        .order_by(Server.domain_id, Server.id)
        .all()
    )

    domains_dict = defaultdict(list)
    for dc in dc_servers:
        domains_dict[dc.domain_id].append(dc)

    return list(domains_dict.values())


def get_domain(domain_id: int, db: Session):
    """
    Récupère le Domain par rapport à son ID

    :param domain_id: ID du domain
    :param db: Session DB
    :return: Domain
    """

    return db.get(Domain, domain_id)
