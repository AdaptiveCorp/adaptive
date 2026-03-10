from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime,Text
from datetime import datetime
from .connection import Base

class DBProject(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deployed = Column(Boolean, default=False)

class DBForest(Base):
    __tablename__ = "forests"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    fqdn = Column(String(255), nullable=False)

class DBDomain(Base):
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    forest_id = Column(Integer, ForeignKey("forests.id"))
    fqdn = Column(String(255), nullable=False)

class DBServer(Base):
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    forest_id = Column(Integer, ForeignKey("forests.id"))
    domain_id = Column(Integer, ForeignKey("domains.id"))
    fqdn = Column(String(255), nullable=False)
    is_dc = Column(Boolean, default=False)
    ip = Column(String(15), nullable=True)
    vm_id = Column(Integer, nullable=True)
    gateway = Column(String(15), nullable=True)
    dns = Column(String(15), nullable=True)

class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    forest_id = Column(Integer, ForeignKey("forests.id"))
    domain_id = Column(Integer, ForeignKey("domains.id"))
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)


class DBVulnerabilityTemplate(Base):
    """
    Catalogue des vulnérabilités disponibles (rempli par les devs)
    """
    __tablename__ = "vulnerability_templates"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    
    powershell_template = Column(Text, nullable=False)
    
    required_params = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class DBAppliedUserVulnerability(Base):
    """
    Instances de vulnérabilités appliquées à des users
    """
    __tablename__ = "applied_vulnerabilities"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    template_id = Column(Integer, ForeignKey("vulnerability_templates.id"))
    
    # Cible de la vulnérabilité
    source_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Paramètres spécifiques (JSON) : {"spn_name": "HTTP/webapp"}
    params = Column(Text)
    
    # Script PowerShell généré (avec les variables remplacées)
    generated_script = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)