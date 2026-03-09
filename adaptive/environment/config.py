from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = "Adaptive"
    db_file: str = "app.db"

    # Proxmox
    proxmox_host: str = ""
    proxmox_user: str = ""
    proxmox_password: str = ""
    proxmox_node: str = "pve-01"
    proxmox_token: str = ""

    # Ansible / Windows
    ansible_user: str = "Administrator"
    ansible_password: str = ""
    dsrm_password: str = ""


settings = Settings()
