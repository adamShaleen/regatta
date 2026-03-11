from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/regatta"
    model_config = {"env_file": ".env"}
    jwt_secret_key: str
    shared_password: str


settings = Settings()  # type: ignore
