class AdaptiveError(Exception):
    """Base exception for all Adaptive errors."""

    def __init__(self, message: str, detail: dict | None = None):
        self.message = message
        self.detail = detail or {}
        super().__init__(message)


class ValidationError(AdaptiveError):
    """Invalid parameters or data."""


class ProxmoxError(AdaptiveError):
    """Generic Proxmox error."""


class ProxmoxConnectionError(ProxmoxError):
    """Cannot connect to the Proxmox API."""

    def __init__(self, host: str, cause: str):
        super().__init__(
            f"Cannot connect to Proxmox at {host}: {cause}",
            detail={"host": host, "cause": cause},
        )


class ProxmoxTaskError(ProxmoxError):
    """A Proxmox task failed."""

    def __init__(self, task_upid: str, exitstatus: str | None):
        super().__init__(
            f"Task {task_upid} failed: {exitstatus}",
            detail={"task_upid": task_upid, "exitstatus": exitstatus},
        )


class ProxmoxTimeoutError(ProxmoxError):
    """A Proxmox task timed out."""

    def __init__(self, task_upid: str, timeout: int):
        super().__init__(
            f"Task {task_upid} timed out after {timeout}s",
            detail={"task_upid": task_upid, "timeout": timeout},
        )


class AnsibleError(AdaptiveError):
    """Generic Ansible error."""


class AnsibleTemplateNotFoundError(AnsibleError):
    """Playbook template not found in the database."""

    def __init__(self, code: str):
        super().__init__(
            f"Template '{code}' not found in database",
            detail={"template_code": code},
        )


class AnsiblePlaybookError(AnsibleError):
    """Playbook execution failed."""


class DeploymentError(AdaptiveError):
    """Deployment orchestration error."""


class ServerMissingTemplateError(ValidationError):
    """Server has no VM template assigned."""

    def __init__(self, server_id: int, fqdn: str):
        super().__init__(
            f"Server '{fqdn}' has no template_vm_id assigned",
            detail={"server_id": server_id, "fqdn": fqdn},
        )


class AnsibleSessionRequiredError(AnsibleError):
    """AnsibleService requires a database session."""

    def __init__(self):
        super().__init__("AnsibleService requires a db session to fetch templates")


class DeploymentNoServersError(DeploymentError):
    """Project has no servers to deploy."""

    def __init__(self, project_name: str):
        super().__init__(
            f"No servers in project '{project_name}'",
            detail={"project": project_name},
        )


class NotFoundError(AdaptiveError):
    """Requested resource does not exist."""


class ConflictError(AdaptiveError):
    """Operation conflicts with existing state."""


class ProjectNotFoundError(NotFoundError):
    """Project does not exist."""

    def __init__(self, project_id: int):
        super().__init__(
            f"Project id={project_id} not found",
            detail={"project_id": project_id},
        )


class ForestNotFoundError(NotFoundError):
    """Forest does not exist."""

    def __init__(self, forest_id: int):
        super().__init__(
            f"Forest id={forest_id} not found",
            detail={"forest_id": forest_id},
        )


class DomainNotFoundError(NotFoundError):
    """Domain does not exist."""

    def __init__(self, domain_id: int):
        super().__init__(
            f"Domain id={domain_id} not found",
            detail={"domain_id": domain_id},
        )


class ServerNotFoundError(NotFoundError):
    """Server does not exist."""

    def __init__(self, server_id: int):
        super().__init__(
            f"Server id={server_id} not found",
            detail={"server_id": server_id},
        )


class VmTemplateNotFoundError(NotFoundError):
    """VM template does not exist."""

    def __init__(self, vm_template_id: int):
        super().__init__(
            f"VmTemplate id={vm_template_id} not found",
            detail={"vm_template_id": vm_template_id},
        )


class VulnerabilityNotFoundError(NotFoundError):
    """Vulnerability template does not exist."""

    def __init__(self, template_id: int):
        super().__init__(
            f"Vulnerability template id={template_id} not found",
            detail={"template_id": template_id},
        )

class VulnerabilityAlreadyExist(ConflictError) :
    """This vulnerability already exist"""
    def __init__(self, applied_vuln_id: int, applied_vuln_code : str, applied_vuln_params : str):
        super().__init__(
            #Changer pour afficher la vuln qui existe déjà
            f"Vulnerability already exist id={applied_vuln_id} already exists",
            detail={"code": applied_vuln_code,"params" : applied_vuln_params},
        )

class AppliedVulnerabilityNotFoundError(NotFoundError):
    """Applied vulnerability does not exist."""

    def __init__(self, applied_id: int):
        super().__init__(
            f"Applied vulnerability id={applied_id} not found",
            detail={"applied_id": applied_id},
        )


class DomainNoDCError(NotFoundError):
    """Domain has no domain controller."""

    def __init__(self, domain_id: int):
        super().__init__(
            f"No domain controller found for domain id={domain_id}",
            detail={"domain_id": domain_id},
        )


class VmTemplateNameConflictError(ConflictError):
    """VM template name already exists."""

    def __init__(self, name: str):
        super().__init__(
            f"VmTemplate with name '{name}' already exists",
            detail={"name": name},
        )


class VmTemplateInUseError(ConflictError):
    """VM template is still referenced by servers."""

    def __init__(self, vm_template_id: int, server_count: int):
        super().__init__(
            f"VmTemplate id={vm_template_id} is still used by {server_count} server(s)",
            detail={"vm_template_id": vm_template_id, "server_count": server_count},
        )


class UserTargetRequiredError(ValidationError):
    """User must be linked to a domain or server."""

    def __init__(self):
        super().__init__("domain_id or server_id is required")


class UserTargetConflictError(ValidationError):
    """User cannot be linked to both a domain and a server."""

    def __init__(self):
        super().__init__("Provide domain_id or server_id, not both")


class VulnerabilityInvalidParamsError(ValidationError):
    """Vulnerability parameters do not match required params."""

    def __init__(self, required_params: str):
        super().__init__(
            f"Invalid parameters, required params are: {required_params}",
            detail={"required_params": required_params},
        )
