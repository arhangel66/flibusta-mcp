"""Dependency injection container."""

from services.client import FlibustaClient
from services.parser import FlibustaParser
from services.service import FlibustaService


def create_flibusta_service() -> FlibustaService:
    """Create configured FlibustaService instance."""
    client = FlibustaClient()
    parser = FlibustaParser()
    return FlibustaService(client=client, parser=parser)