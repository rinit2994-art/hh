"""
Configuration Management for Market Data Fetcher
=================================================

Handles API keys and configuration settings.

Usage:
------
1. Create a .env file in the project root with your API keys:

   FINNHUB_API_KEY=your_finnhub_key_here
   FMP_API_KEY=your_fmp_key_here

2. Import and use in your code:

   from config import Config

   config = Config()
   fetcher = MarketDataFetcher(
       finnhub_api_key=config.FINNHUB_API_KEY,
       fmp_api_key=config.FMP_API_KEY
   )
"""

import os
from typing import Optional


class Config:
    """Configuration class for API keys and settings"""

    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration

        Parameters:
        -----------
        env_file : str
            Path to .env file (default: ".env")
        """
        self.env_file = env_file
        self._load_env()

        # API Keys
        self.FINNHUB_API_KEY = self._get_env("FINNHUB_API_KEY")
        self.FMP_API_KEY = self._get_env("FMP_API_KEY")

        # Data Fetcher Settings
        self.PREFERRED_SOURCE = self._get_env("PREFERRED_SOURCE", "yfinance")
        self.CACHE_TIMEOUT = int(self._get_env("CACHE_TIMEOUT", "300"))  # 5 minutes
        self.MAX_RETRIES = int(self._get_env("MAX_RETRIES", "4"))
        self.RETRY_DELAY = float(self._get_env("RETRY_DELAY", "2.0"))

        # Rate Limiting
        self.YFINANCE_RATE_LIMIT = int(self._get_env("YFINANCE_RATE_LIMIT", "60"))
        self.FINNHUB_RATE_LIMIT = int(self._get_env("FINNHUB_RATE_LIMIT", "60"))
        self.FMP_RATE_LIMIT = int(self._get_env("FMP_RATE_LIMIT", "250"))

    def _load_env(self):
        """Load environment variables from .env file"""
        if not os.path.exists(self.env_file):
            return

        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    os.environ[key] = value

    def _get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default"""
        return os.environ.get(key, default)

    def validate(self) -> bool:
        """
        Validate configuration

        Returns:
        --------
        bool : True if at least one data source is configured
        """
        has_finnhub = self.FINNHUB_API_KEY is not None
        has_fmp = self.FMP_API_KEY is not None

        if not has_finnhub and not has_fmp:
            print("⚠️ No API keys configured. Will use yfinance only.")
            return True

        return True

    def print_config(self):
        """Print current configuration (hides API keys)"""
        print("\n" + "="*60)
        print("CONFIGURATION")
        print("="*60)

        # API Keys (masked)
        print("\nAPI Keys:")
        if self.FINNHUB_API_KEY:
            masked = self.FINNHUB_API_KEY[:4] + "..." + self.FINNHUB_API_KEY[-4:]
            print(f"  Finnhub: {masked}")
        else:
            print("  Finnhub: Not configured")

        if self.FMP_API_KEY:
            masked = self.FMP_API_KEY[:4] + "..." + self.FMP_API_KEY[-4:]
            print(f"  FMP: {masked}")
        else:
            print("  FMP: Not configured")

        # Settings
        print("\nSettings:")
        print(f"  Preferred Source: {self.PREFERRED_SOURCE}")
        print(f"  Cache Timeout: {self.CACHE_TIMEOUT}s")
        print(f"  Max Retries: {self.MAX_RETRIES}")
        print(f"  Retry Delay: {self.RETRY_DELAY}s")

        # Rate Limits
        print("\nRate Limits (calls per minute):")
        print(f"  yfinance: {self.YFINANCE_RATE_LIMIT}")
        print(f"  Finnhub: {self.FINNHUB_RATE_LIMIT}")
        print(f"  FMP: {self.FMP_RATE_LIMIT}")

        print("="*60)

    def to_dict(self) -> dict:
        """Export configuration as dictionary (excluding API keys)"""
        return {
            'preferred_source': self.PREFERRED_SOURCE,
            'cache_timeout': self.CACHE_TIMEOUT,
            'max_retries': self.MAX_RETRIES,
            'retry_delay': self.RETRY_DELAY,
            'rate_limits': {
                'yfinance': self.YFINANCE_RATE_LIMIT,
                'finnhub': self.FINNHUB_RATE_LIMIT,
                'fmp': self.FMP_RATE_LIMIT
            },
            'has_finnhub_key': self.FINNHUB_API_KEY is not None,
            'has_fmp_key': self.FMP_API_KEY is not None
        }


# Singleton instance
_config_instance = None


def get_config(reload: bool = False) -> Config:
    """
    Get configuration singleton

    Parameters:
    -----------
    reload : bool
        Force reload configuration from file

    Returns:
    --------
    Config : Configuration instance
    """
    global _config_instance

    if _config_instance is None or reload:
        _config_instance = Config()

    return _config_instance


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║          ⚙️  CONFIGURATION MANAGEMENT                         ║
║                                                              ║
║  Manages API keys and settings for Market Data Fetcher      ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Test configuration
    config = get_config()
    config.validate()
    config.print_config()

    print("\nConfiguration as dict:")
    print(config.to_dict())
