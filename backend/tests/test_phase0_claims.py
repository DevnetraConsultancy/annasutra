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
    """Verify landing page preserves C-DAC / MeitY header & footer and displays * DEMO DATA footnote below simulator."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.content.decode("utf-8")

    # Favicon and official C-DAC / MeitY attribution preserved
    assert "/favicon.ico" in html
    assert "Centre for Development of Advanced Computing (C-DAC)" in html
    assert "Ministry of Electronics & Information Technology, Government of India" in html
    assert "© 2026 AnnaSutra • Developed & Maintained by C-DAC, Ministry of Electronics & IT (MeitY), Government of India." in html
    assert "* DEMO DATA — Simulated Demonstration (Not real transactions)" in html


@pytest.mark.django_db
def test_public_lot_view_claims_scrubbed(client):
    """Verify public lot summary/not found templates preserve C-DAC / MeitY footer attribution."""
    resp = client.get("/public/lot/7K3Q9XMD4T2B/")
    assert resp.status_code == 404
    html = resp.content.decode("utf-8")

    assert "Centre for Development of Advanced Computing (C-DAC)" in html
    assert "Ministry of Electronics & Information Technology, Government of India" in html
    assert "© 2026 AnnaSutra • Developed & Maintained by C-DAC, Ministry of Electronics & IT (MeitY), Government of India." in html
