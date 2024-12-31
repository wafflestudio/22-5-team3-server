from pydantic_settings import BaseSettings, SettingsConfigDict
from snuvote.settings import SETTINGS


class DatabaseSettings(BaseSettings):
    dialect: str = ""
    driver: str = ""
    host: str = ""
    port: int = 0
    user: str = ""
    password: str = ""
    database: str = ""

    @property
    def url(self) -> str:
        return f"mysql+pymysql://admin:{self.password}@{self.host}:3306/snuvote"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="DB_",
        env_file=SETTINGS.env_file,
    )


DB_SETTINGS = DatabaseSettings()
