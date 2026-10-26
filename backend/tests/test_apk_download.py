import pytest
from rest_framework import status

@pytest.mark.django_db
def test_apk_download_redirect(client):
    """Verify that /download/apk and /download/android redirect to the official APK release."""
    resp = client.get("/download/apk")
    assert resp.status_code == status.HTTP_302_FOUND
    assert "github.com" in resp.url
    assert "app-debug.apk" in resp.url

    resp_slash = client.get("/download/apk/")
    assert resp_slash.status_code == status.HTTP_302_FOUND
    assert "github.com" in resp_slash.url

    resp_android = client.get("/download/android")
    assert resp_android.status_code == status.HTTP_302_FOUND
    assert "github.com" in resp_android.url
