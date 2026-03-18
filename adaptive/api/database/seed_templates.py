import json
import logging
from pathlib import Path

import yaml

from adaptive.api.environment.database import Base, SessionLocal, engine
from adaptive.api.models.template import Template

logger = logging.getLogger(__name__)


def load_templates_from_yaml(yaml_path: str | None = None) -> list[dict]:
    if yaml_path is None:
        yaml_path = str(Path(__file__).parent / "templates.yaml")

    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["templates"]


def seed_templates(yaml_path: str | None = None) -> None:
    db = SessionLocal()

    templates = load_templates_from_yaml(yaml_path)

    added_count = 0
    updated_count = 0

    for tpl_data in templates:
        existing = db.query(Template).filter(Template.code == tpl_data["code"]).first()

        required_params_json = json.dumps(tpl_data.get("required_params", []))

        if existing:
            existing.name = tpl_data["name"]
            existing.type = tpl_data["type"]
            existing.description = tpl_data["description"]
            existing.category = tpl_data["category"]
            existing.content = tpl_data["content"]
            existing.required_params = required_params_json
            updated_count += 1
        else:
            tpl = Template(
                code=tpl_data["code"],
                name=tpl_data["name"],
                type=tpl_data["type"],
                description=tpl_data["description"],
                category=tpl_data["category"],
                content=tpl_data["content"],
                required_params=required_params_json,
            )
            db.add(tpl)
            added_count += 1

    db.commit()
    logger.info("Templates : %d ajoutés, %d mis à jour", added_count, updated_count)
    print(f"Templates : {added_count} ajoutés, {updated_count} mis à jour")
    db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_templates()
