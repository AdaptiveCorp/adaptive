import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ansible_runner
from sqlalchemy.orm import Session

from adaptive.api.environment.config import settings
from adaptive.api.exceptions import AnsibleSessionRequiredError, AnsibleTemplateNotFoundError
from adaptive.api.models.template import Template

logger = logging.getLogger(__name__)

PREFIX = "[ANSIBLE]"


@dataclass
class PlaybookResult:
    success: bool
    stdout: str = ""
    return_code: int | None = None
    error: str | None = None


class AnsibleService:
    def __init__(
        self,
        db: Session | None = None,
        user: str | None = None,
        password: str | None = None,
        dsrm_password: str | None = None,
    ):
        self._db = db
        self._user = user or settings.ansible_user
        self._password = password or settings.ansible_password
        self._dsrm_password = dsrm_password or settings.dsrm_password
        logger.info("%s Service initialized (user=%s)", PREFIX, self._user)

    def _get_template_content(self, code: str) -> str:
        if not self._db:
            raise AnsibleSessionRequiredError()

        template = self._db.query(Template).filter(Template.code == code).first()
        if not template:
            raise AnsibleTemplateNotFoundError(code)

        logger.info("%s Fetched template '%s' from database", PREFIX, code)
        return template.content

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
            "%s Promoting DC '%s' (%s) for domain '%s' (first_dc=%s)",
            PREFIX,
            dc_hostname,
            server_ip,
            domain_fqdn,
            is_first_dc,
        )

        extravars: dict[str, Any] = {
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

        content = self._get_template_content("dc_promo")
        result = self._run_playbook(content, server_ip, extravars)

        if result.success:
            logger.info("%s DC promotion succeeded for '%s'", PREFIX, dc_hostname)
        else:
            logger.error("%s DC promotion failed for '%s': %s", PREFIX, dc_hostname, result.error)

        return result

    def add_users(
        self, server_ip: str, users: list[dict[str, str]], base_dn: str, domain_fqdn: str
    ) -> PlaybookResult:
        logger.info("%s Adding %d user(s) on %s", PREFIX, len(users), server_ip)

        extravars: dict[str, Any] = {
            "target_host": server_ip,
            "users_list": users,
            "base_dn": base_dn,
            "domain_fqdn": domain_fqdn,
        }

        content = self._get_template_content("add_users")
        result = self._run_playbook(content, server_ip, extravars)

        if result.success:
            logger.info("%s Successfully added %d user(s) on %s", PREFIX, len(users), server_ip)
        else:
            logger.error("%s Failed to add users on %s: %s", PREFIX, server_ip, result.error)

        return result

    def delete_user(
        self,
        server_ip: str,
        username: str,
    ) -> PlaybookResult:
        logger.info("%s Deleting user '%s' on %s", PREFIX, username, server_ip)

        extravars: dict[str, Any] = {
            "target_host": server_ip,
            "username": username,
        }

        content = self._get_template_content("delete_user_by_sam")
        result = self._run_playbook(content, server_ip, extravars)

        if result.success:
            logger.info("%s User '%s' deleted successfully on %s", PREFIX, username, server_ip)
        else:
            logger.error("%s Failed to delete user '%s' on %s: %s", PREFIX, username, server_ip, result.error)

        return result

    def add_groups(
        self,
        server_ip: str,
        groups: list[dict[str, str]],
        base_dn: str,
        domain_fqdn: str,
    ) -> PlaybookResult:
        logger.info("%s Adding %d group(s) on %s", PREFIX, len(groups), server_ip)

        extravars: dict[str, Any] = {
            "target_host": server_ip,
            "groups_list": groups,
            "base_dn": base_dn,
            "domain_fqdn": domain_fqdn,
        }

        content = self._get_template_content("add_groups")
        result = self._run_playbook(content, server_ip, extravars)

        if result.success:
            logger.info("%s Successfully added %d group(s) on %s", PREFIX, len(groups), server_ip)
        else:
            logger.error("%s Failed to add groups on %s: %s", PREFIX, server_ip, result.error)

        return result

    def add_group_members(
        self,
        server_ip: str,
        memberships: list[dict[str, Any]],
    ) -> PlaybookResult:
        logger.info(
            "%s Adding members to %d group(s) on %s",
            PREFIX, len(memberships), server_ip
        )

        # memberships contient toujours 1 seul élément désormais
        membership = memberships[0]

        extravars: dict[str, Any] = {
            "target_host": server_ip,
            "group_name": membership["group_name"],
            "members": membership["members"],
        }

        content = self._get_template_content("add_group_members")
        result = self._run_playbook(content, server_ip, extravars)

        if result.success:
            logger.info("%s Successfully updated group memberships on %s", PREFIX, server_ip)
        else:
            logger.error("%s Failed to update group memberships on %s: %s", PREFIX, server_ip, result.error)

        return result
    
    
    def _run_playbook(
        self,
        playbook_content: str,
        target_host: str,
        extravars: dict[str, Any],
    ) -> PlaybookResult:
        logger.info("%s Running playbook on %s", PREFIX, target_host)

        print("PASSWORD : ", self._password)
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
        merged_extravars = {
            "ansible_connection": "winrm",
            "ansible_winrm_transport": "basic",
            "ansible_winrm_scheme": "http",
            "ansible_winrm_server_cert_validation": "ignore",
            "ansible_port": 5985,
            **extravars, 
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()
            playbook_path = project_dir / "playbook.yaml"
            playbook_path.write_text(playbook_content, encoding="utf-8")

            result = ansible_runner.run(
                private_data_dir=tmpdir,
                playbook="playbook.yaml",
                inventory=inventory,
                extravars=merged_extravars,
                verbosity=2,
            )

            stdout = result.stdout.read() if result.stdout else ""

            if result.status == "successful":
                logger.info("%s Playbook completed successfully (rc=%s)", PREFIX, result.rc)
                return PlaybookResult(success=True, stdout=stdout, return_code=result.rc)

            logger.error("%s Playbook failed (rc=%s)", PREFIX, result.rc)
            return PlaybookResult(
                success=False,
                stdout=stdout,
                return_code=result.rc,
                error=stdout or "Unknown error",
            )
