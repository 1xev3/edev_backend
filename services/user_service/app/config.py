from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


from typing import Tuple, Type

from pydantic import Field, PostgresDsn, SecretStr, FilePath

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    PG_ASYNC_DSN: PostgresDsn = Field(
        default = 'postgres://user:pass@localhost:5432/foobar',
    )

    JWT_SECRET: SecretStr = Field(
        alias='JWT_SECRET'
    )

    JWT_REFRESH_SECRET: SecretStr = Field(
        alias='JWT_REFRESH_SECRET'
    )

    DEFAULT_GROUPS_CONFIG_PATH: FilePath = Field(
        default='default-groups.json',
        alias='DEFAULT_GROUPS_CONFIG_PATH'
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return dotenv_settings, env_settings, init_settings

def load_config(*arg, **vararg) -> Config:
    return Config(*arg, **vararg)