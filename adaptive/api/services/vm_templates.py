import os
import subprocess
from datetime import datetime

from adaptive.api.environment.config import Settings
from adaptive.api.models.vm_template import VmTemplate


def deploy_vm_template(vm_template: VmTemplate):
    cwd = Settings().packer_template_path / vm_template.name

    log_path = cwd / f"packer-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

    packer_env = {
        **os.environ,
        "PACKER_LOG": "1",
        "PACKER_LOG_PATH": str(log_path),
    }

    result: subprocess.CompletedProcess[bytes] = subprocess.run(
        ["packer", "validate", "."],
        cwd=cwd,
        env=packer_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if result.returncode != 0:
        raise ValueError("Packer template validation failed")

    _ = subprocess.Popen(
        ["packer", "build", "."],
        cwd=cwd,
        env=packer_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return "OK"
