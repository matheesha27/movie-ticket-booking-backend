from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    mail_username: str
    mail_password: str
    mail_from: str

    secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"


settings = Settings()
