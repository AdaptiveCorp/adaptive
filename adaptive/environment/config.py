from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Adaptive"

    db_file: str = "adaptive.db"

    proxmox_user: str = ""
    proxmox_password: str = ""
    proxmox_token: str = ""
    proxmox_endpoint: str = ""


settings = Settings()
