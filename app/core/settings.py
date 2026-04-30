from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # database configuration
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    # server configuration
    server_host: str
    server_port: int

    # JWT configuration
    jwt_secret_key_access: str
    jwt_secret_key_refresh: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int

    # SuperAdmin configuration
    superadmin_password: str
    superadmin_first_name: str
    superadmin_last_name: str

    class Config:
        env_file = ".env"


settings = Settings()
