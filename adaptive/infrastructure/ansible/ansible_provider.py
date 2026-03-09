import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

import ansible_runner  # type: ignore

from adaptive.environment.config import settings

logger = logging.getLogger(__name__)

PLAYBOOKS_DIR = Path(__file__).parent.parent.parent / "ansible" / "inventory" / "playbooks"


@dataclass
class PlaybookResult:
    success: bool
    stdout: str = ""
    return_code: int | None = None
    error: str | None = None


class AnsibleService:
    def __init__(
        self,
        user: str | None = None,
        password: str | None = None,
        dsrm_password: str | None = None,
    ):
        self._user = user or settings.ansible_user
        self._password = password or settings.ansible_password
        self._dsrm_password = dsrm_password or settings.dsrm_password

    def dc_promote(
        self,
        server_ip: str,
        dc_hostname: str,
        domain_fqdn: str,
        domain_netbios: str,
        is_first_dc: bool = True,
        domain_admin: str | None = None,
        forest_mode: str = "WinThreshold",
        domain_mode: str = "WinThreshold",
        install_dns: bool = True,
    ) -> PlaybookResult:
        logger.info(
            "Promoting DC %s (%s) for domain %s (first=%s)",
            dc_hostname, server_ip, domain_fqdn, is_first_dc,
        )

        extravars = {
            "target_host": server_ip,
            "dc_hostname": dc_hostname,
            "domain_fqdn": domain_fqdn,
            "domain_netbios": domain_netbios,
            "dsrm_password": self._dsrm_password,
            "is_first_dc": is_first_dc,
            "forest_mode": forest_mode,
            "domain_mode": domain_mode,
            "install_dns": install_dns,
            "domain_admin": domain_admin or f"Administrator@{domain_fqdn}",
        }

        return self._run_playbook("dc_promo.yaml", server_ip, extravars)

    def add_users(
        self,
        server_ip: str,
        users: list[dict],
    ) -> PlaybookResult:
        logger.info("Adding %d users on %s", len(users), server_ip)

        extravars = {
            "target_host": server_ip,
            "users": users,
        }

        return self._run_playbook("add_users.yaml", server_ip, extravars)

    def _run_playbook(
        self,
        playbook_name: str,
        target_host: str,
        extravars: dict,
    ) -> PlaybookResult:
        playbook_path = PLAYBOOKS_DIR / playbook_name
        if not playbook_path.exists():
            raise FileNotFoundError(f"Playbook not found: {playbook_path}")

        inventory = {
            "all": {
                "hosts": {
                    target_host: {
                        "ansible_user": self._user,
                        "ansible_password": self._password,
                    }
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = ansible_runner.run(
                private_data_dir=tmpdir,
                playbook=str(playbook_path),
                inventory=inventory,
                extravars=extravars,
                verbosity=2,
            )

            stdout = result.stdout.read() if result.stdout else ""

            if result.status == "successful":
                logger.info("Playbook %s completed successfully", playbook_name)
                return PlaybookResult(success=True, stdout=stdout, return_code=result.rc)

            logger.error("Playbook %s failed: %s", playbook_name, stdout)
            return PlaybookResult(
                success=False,
                stdout=stdout,
                return_code=result.rc,
                error=stdout or "Unknown error",
            )
