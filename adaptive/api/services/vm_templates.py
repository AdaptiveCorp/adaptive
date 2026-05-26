import logging
import os
import subprocess
from datetime import datetime

from adaptive.api.environment.config import Settings
from adaptive.api.models.vm_template import VmTemplate

logger = logging.getLogger(__name__)

_running_builds: set[int] = set()


def deploy_vm_template(vm_template: VmTemplate):
    if vm_template.id in _running_builds:
        raise ValueError(f"A build is already running for template {vm_template.name}")

    cwd = Settings().packer_template_path / vm_template.name

    log_path = cwd / f"packer-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

    packer_env = {
        **os.environ,
        "PACKER_LOG": "1",
        "PACKER_LOG_PATH": str(log_path),
    }

    var_file = cwd / "variables.pkrvars.hcl"
    packer_args_suffix = ["--var-file", str(var_file)] if var_file.exists() else []

    result: subprocess.CompletedProcess[bytes] = subprocess.run(
        ["packer", "validate", *packer_args_suffix, "."],
        cwd=cwd,
        env=packer_env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(
            "packer validate failed (vm_template=%s):\nstdout: %s\nstderr: %s",
            vm_template.name,
            result.stdout,
            result.stderr,
        )
        raise ValueError(f"Packer template validation failed: {result.stderr or result.stdout}")

    _running_builds.add(vm_template.id)

    def _run():
        try:
            subprocess.run(
                ["packer", "build", *packer_args_suffix, "."],
                cwd=cwd,
                env=packer_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        finally:
            _running_builds.discard(vm_template.id)

    import threading

    threading.Thread(target=_run, daemon=True).start()

    return "OK"
