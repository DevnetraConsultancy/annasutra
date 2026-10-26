import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_mobile_preview_renders(client):
    """Verify that /mobile/ and /app/ render the mobile preview simulator with HTTP 200."""
    response = client.get(reverse("mobile_preview"))
    assert response.status_code == status.HTTP_200_OK
    assert b"AnnaSutra Mobile" in response.content
    assert b"Download Android APK" in response.content
    assert b"50MB" in response.content


@pytest.mark.django_db
def test_mobile_preview_app_alias(client):
    """Verify that /app/ alias renders the mobile preview simulator."""
    response = client.get(reverse("mobile_app"))
    assert response.status_code == status.HTTP_200_OK
    assert b"device-shell" in response.content
