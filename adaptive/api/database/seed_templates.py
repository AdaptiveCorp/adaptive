import json
import logging
import uuid
from pathlib import Path

import yaml

from adaptive.api.environment.database import Base, SessionLocal, engine
from adaptive.api.models.template import Template
from adaptive.api.models.vm_template import VmTemplate, VmTemplateStatus

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
                reverse_type=tpl_data["reverse_type"],
                reverse_content=tpl_data["reverse_content"],
                required_params=required_params_json,
            )
            db.add(tpl)
            added_count += 1

    db.commit()
    logger.info("Templates : %d ajoutés, %d mis à jour", added_count, updated_count)
    db.close()


def seed_vm_templates(yaml_path: str | None = None) -> None:
    db = SessionLocal()

    vm_templates = load_templates_from_yaml(yaml_path)

    added_count = 0
    updated_count = 0

    for tpl_data in vm_templates:
        existing = db.query(VmTemplate).filter(VmTemplate.vm_id == tpl_data["vm_id"]).first()

        if existing:
            existing.name = tpl_data["name"]
            existing.description = tpl_data["description"]
            existing.vm_id = tpl_data["vm_id"]
            existing.vm_uuid = uuid.uuid4()
            existing.status = VmTemplateStatus.UNINSTALL
            updated_count += 1
        else:
            tpl = VmTemplate(
                name=tpl_data["name"],
                description=tpl_data["description"],
                vm_id=tpl_data["vm_id"],
                vm_uuid=tpl_data["vm_uuid"],
                status=VmTemplateStatus.UNINSTALL,
            )
            db.add(tpl)
            added_count += 1

    db.commit()
    logger.info("Templates : %d ajoutés, %d mis à jour", added_count, updated_count)
    db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_templates()
    seed_vm_templates("vm-templates.yaml")
