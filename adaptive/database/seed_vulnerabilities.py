import yaml
import json
from pathlib import Path
from .connection import SessionLocal, engine, Base
from .orm_models import DBVulnerabilityTemplate

def load_vulnerabilities_from_yaml(yaml_path: str = "/home/zleb/Secu/ENSIBS/4A/PROJET/Adaptive_backend/src/lab_ad/database/vulnerabilities.yaml"):
    """
    Charge les vulnérabilités depuis le fichier YAML
    """
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['vulnerabilities']

def seed_vulnerability_templates():
    """
    Lit le fichier YAML et peuple la base de données
    """
    db = SessionLocal()
    
    # Charger les vulns depuis YAML
    vulnerabilities = load_vulnerabilities_from_yaml()
    
    added_count = 0
    updated_count = 0
    
    for vuln_data in vulnerabilities:
        # Vérifier si existe déjà
        existing = db.query(DBVulnerabilityTemplate).filter(
            DBVulnerabilityTemplate.code == vuln_data["code"]
        ).first()
        
        # Convertir required_params en JSON
        required_params_json = json.dumps(vuln_data.get("required_params", []))
        
        if existing:
            # Mettre à jour si existe
            existing.name = vuln_data["name"]
            existing.description = vuln_data["description"]
            existing.category = vuln_data["category"]
            existing.powershell_template = vuln_data["powershell_template"]
            existing.required_params = required_params_json
            updated_count += 1
        else:
            # Créer si n'existe pas
            vuln = DBVulnerabilityTemplate(
                code=vuln_data["code"],
                name=vuln_data["name"],
                description=vuln_data["description"],
                category=vuln_data["category"],
                powershell_template=vuln_data["powershell_template"],
                required_params=required_params_json
            )
            db.add(vuln)
            added_count += 1
    
    db.commit()
    print(f"Vulnérabilités : {added_count} ajoutées, {updated_count} mises à jour")
    db.close()

if __name__ == "__main__":
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    # Peupler depuis YAML
    seed_vulnerability_templates()
