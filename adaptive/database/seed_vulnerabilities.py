import json
from pathlib import Path

import yaml

from adaptive.environment.database import SessionLocal, engine, Base
from adaptive.models.vulnerability import Vulnerability


def load_vulnerabilities_from_yaml(yaml_path: str | None = None):
    """
    Charge les vulnérabilités depuis le fichier YAML
    """
    if yaml_path is None:
        yaml_path = str(Path(__file__).parent / "vulnerabilities.yaml")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["vulnerabilities"]


def seed_vulnerability_templates(yaml_path: str | None = None):
    """
    Lit le fichier YAML et peuple la base de données
    """
    db = SessionLocal()

    vulnerabilities = load_vulnerabilities_from_yaml(yaml_path)

    added_count = 0
    updated_count = 0

    for vuln_data in vulnerabilities:
        existing = db.query(Vulnerability).filter(
            Vulnerability.code == vuln_data["code"]
        ).first()

        required_params_json = json.dumps(vuln_data.get("required_params", []))

        if existing:
            existing.name = vuln_data["name"]
            existing.description = vuln_data["description"]
            existing.category = vuln_data["category"]
            existing.powershell_template = vuln_data["powershell_template"]
            existing.required_params = required_params_json
            updated_count += 1
        else:
            vuln = Vulnerability(
                code=vuln_data["code"],
                name=vuln_data["name"],
                description=vuln_data["description"],
                category=vuln_data["category"],
                powershell_template=vuln_data["powershell_template"],
                required_params=required_params_json,
            )
            db.add(vuln)
            added_count += 1

    db.commit()
    print(f"Vulnérabilités : {added_count} ajoutées, {updated_count} mises à jour")
    db.close()


if __name__ == "__main__":
    import adaptive.models.applied_vulnerability  # noqa: F401 - enregistre les modèles sur Base
    Base.metadata.create_all(bind=engine)
    seed_vulnerability_templates()
