import logging
import subprocess

from adaptive.api.environment.config import settings
from adaptive.api.models.vm_template import VmTemplate

logger = logging.getLogger(__name__)


def deploy_vm_template(vm_template: VmTemplate):
    result: subprocess.CompletedProcess[bytes] = subprocess.run(
        ["packer", "validate", "."],
        cwd=settings.packer_template_path / vm_template.name,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if result.returncode != 0:
        raise ValueError("Packer template validation failed")

    _ = subprocess.Popen(
        ["packer", "build", "."],
        cwd=settings.packer_template_path / vm_template.name,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return "OK"
