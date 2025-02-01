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
    alembic_prefix: str | None = None

    def __init__(self, prefix: str|None = None):
        super().__init__()
        self.alembic_prefix = prefix

    @property
    def url(self) -> str:
        if self.alembic_prefix == "alembic":
            return f"mysql+pymysql://admin:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"mysql+aiomysql://admin:{self.password}@{self.host}:{self.port}/{self.database}"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="DB_",
        env_file=SETTINGS.env_file,
        extra = 'ignore'
    )


DB_SETTINGS = DatabaseSettings()
DB_ALEMBIC_SETTINGS = DatabaseSettings('alembic')
