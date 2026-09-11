"""
Configuration — load environment variables and app-wide settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Server identity
    SERVER_NAME: str = os.getenv("SERVER_NAME", "Friday")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # External API keys
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    def validate_environment(self) -> list[str]:
        required_keys = {
            "LIVEKIT_URL": self.LIVEKIT_URL,
            "LIVEKIT_API_KEY": self.LIVEKIT_API_KEY,
            "LIVEKIT_API_SECRET": self.LIVEKIT_API_SECRET,
            "GOOGLE_API_KEY": self.GOOGLE_API_KEY,
            "SARVAM_API_KEY": self.SARVAM_API_KEY,
            "OPENAI_API_KEY": self.OPENAI_API_KEY,
        }
        missing = [k for k, v in required_keys.items() if not v or "your-" in v]
        return missing


config = Config()

