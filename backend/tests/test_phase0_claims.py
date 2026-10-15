"""Unit tests validating Phase 0 false claim cleanup and favicon integration."""

import pytest


@pytest.mark.django_db
def test_favicon_endpoint(client):
    """Verify /favicon.ico serves the new brand favicon asset."""
    resp = client.get("/favicon.ico")
    assert resp.status_code == 200
    content = b"".join(resp.streaming_content) if hasattr(resp, "streaming_content") else resp.content
    assert len(content) > 0
    assert resp.headers.get("Content-Type") in ["image/x-icon", "image/vnd.microsoft.icon"]


@pytest.mark.django_db
def test_landing_page_claims_scrubbed(client):
    """Verify that all unverified claims and government logos have been removed from landing page."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.content.decode("utf-8")

    # Mandatory disclaimers present
    assert "AnnaSutra: produce traceability (pilot)" in html
    assert "AnnaSutra is an independent project. It is not a government service." in html
    assert "/favicon.ico" in html

    # Unverified claims purged
    assert "Developed & Maintained by C-DAC" not in html
    assert "Ministry of Electronics & IT (MeitY)" not in html
    assert "1800-180-1551" not in html
    assert "1915" not in html
    assert "1800-425-CDAC" not in html
    assert "DPDP Act 2023 Certified" not in html
    assert "1,42,850+" not in html
    assert "2,480+" not in html


@pytest.mark.django_db
def test_public_lot_view_claims_scrubbed(client):
    """Verify that public lot summary/not found templates also have false claims removed."""
    resp = client.get("/public/lot/7K3Q9XMD4T2B/")
    # 404 since it's an unpopulated lot, but renders lot_not_found.html template
    assert resp.status_code == 404
    html = resp.content.decode("utf-8")

    assert "AnnaSutra is an independent project. It is not a government service." in html
    assert "Developed & Maintained by C-DAC" not in html
    assert "1800-180-1551" not in html
    assert "1915" not in html
    assert "1800-425-CDAC" not in html
    assert "DPDP Act 2023 Certified" not in html
