"""Contract tests validating Django URLs and responses against api/openapi.yaml."""
from pathlib import Path
import yaml
import pytest
from django.urls import resolve, Resolver404
from openapi_spec_validator import validate_spec


@pytest.fixture(scope="module")
def openapi_spec():
    root = Path(__file__).resolve().parent.parent.parent
    spec_path = root / "api" / "openapi.yaml"
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    # Validate OpenAPI 3.0.3 schema
    validate_spec(spec)
    return spec


def test_openapi_spec_is_valid(openapi_spec):
    """Ensure the specification itself is valid OpenAPI 3.0.3."""
    assert openapi_spec["openapi"].startswith("3.0")
    assert "paths" in openapi_spec
    assert len(openapi_spec["paths"]) >= 35


def test_all_openapi_paths_exist_in_django(openapi_spec):
    """Ensure every path documented in api/openapi.yaml is mapped in Django URLs."""
    paths = openapi_spec["paths"]
    missing_paths = []

    for path in paths:
        # Replace OpenAPI path parameters with dummy values for resolver testing
        test_path = path
        test_path = test_path.replace("{device_id}", "00000000-0000-0000-0000-000000000000")
        test_path = test_path.replace("{org_id}", "00000000-0000-0000-0000-000000000000")
        test_path = test_path.replace("{code}", "7K3Q9XMD4T2B")
        test_path = test_path.replace("{handover_id}", "00000000-0000-0000-0000-000000000000")
        test_path = test_path.replace("{event_id}", "00000000-0000-0000-0000-000000000000")
        test_path = test_path.replace("{recall_id}", "00000000-0000-0000-0000-000000000000")

        # Strip leading slash for django resolve
        url_to_test = test_path.lstrip("/")
        try:
            match = resolve("/" + url_to_test)
            assert match is not None
        except Resolver404:
            missing_paths.append(path)

    assert not missing_paths, f"The following OpenAPI paths are missing in Django: {missing_paths}"
