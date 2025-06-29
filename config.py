"""Configuration settings for Flibusta MCP."""

import os
from pathlib import Path


class Config:
    """Configuration class for Flibusta MCP server."""
    
    # Default download directory
    DEFAULT_DOWNLOAD_DIR = Path.home() / "Documents" / "books"
    
    # Get download directory from environment variable or use default
    DOWNLOAD_DIR = Path(os.getenv("FLIBUSTA_DOWNLOAD_DIR", DEFAULT_DOWNLOAD_DIR))
    
    # Flibusta base URL
    BASE_URL = os.getenv("FLIBUSTA_BASE_URL", "https://flibusta.is")
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = int(os.getenv("FLIBUSTA_TIMEOUT", "30"))
    
    # User agent for requests
    USER_AGENT = os.getenv(
        "FLIBUSTA_USER_AGENT", "Mozilla/5.0 (compatible; BookBot/1.0)"
    )


# Global config instance
config = Config()