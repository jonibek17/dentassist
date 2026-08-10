import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    ADMIN_CHAT_ID: str = os.getenv("ADMIN_CHAT_ID", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    CLINIC_DATA_PATH: str = os.path.join(DATA_DIR, "clinic.json")
    DB_PATH: str = os.path.join(BASE_DIR, "appointments.db")


config = Config()
