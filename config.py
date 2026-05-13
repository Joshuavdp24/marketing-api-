from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    anthropic_api_key: str
    valid_api_keys: str
    model: str = "claude-sonnet-4-6"

    def get_api_keys(self) -> set[str]:
        return {k.strip() for k in self.valid_api_keys.split(",")}


settings = Settings()
