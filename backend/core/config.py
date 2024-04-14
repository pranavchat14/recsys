from pydantic_settings import BaseSettings
from dotenv import find_dotenv


class Settings(BaseSettings):
    database_url: str

    class Config:
        dot_path = find_dotenv(".env")
        env_file = dot_path
