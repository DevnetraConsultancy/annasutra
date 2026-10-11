"""Pytest fixtures for AnnaSutra backend tests."""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()
