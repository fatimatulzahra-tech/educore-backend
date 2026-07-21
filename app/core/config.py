from dotenv import load_dotenv

import os

load_dotenv()


class Settings:

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    ALGORITHM = os.getenv(
        "ALGORITHM"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES = 15

    REFRESH_TOKEN_EXPIRE_DAYS = 7

    DATABASE_URL = os.getenv(
        "DATABASE_URL"
    )


settings = Settings()