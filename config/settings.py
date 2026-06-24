from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    stripe_secret_key: str = "sk_test_mock"
    stripe_webhook_secret: str = "whsec_mock"
    stripe_price_pro_monthly: str = "price_pro_monthly_mock"
    stripe_price_pro_annual: str = "price_pro_annual_mock"
    stripe_price_team_monthly: str = "price_team_monthly_mock"
    stripe_price_enterprise: str = "price_enterprise_mock"

    model_config = {
        "env_prefix": "STRIPE_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()
