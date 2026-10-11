"""RFC 7807 Problem Details exception handler conforming to api/openapi.yaml."""
from typing import Any
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def problem_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        detail = ""
        code = "ERROR"

        if isinstance(response.data, dict):
            detail = str(response.data.get("detail", response.data))
            code = response.data.get("code", "ERROR")
        elif isinstance(response.data, list):
            detail = "; ".join(str(item) for item in response.data)
        else:
            detail = str(response.data)

        problem_data = {
            "type": f"https://api.example.in/errors/{status_code}",
            "title": response.status_text if hasattr(response, "status_text") else "Error",
            "status": status_code,
            "detail": detail,
            "code": code,
        }
        response.data = problem_data
        response["Content-Type"] = "application/problem+json"
    else:
        # Unhandled server errors (500)
        problem_data = {
            "type": "https://api.example.in/errors/500",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "An unexpected server error occurred.",
            "code": "INTERNAL_SERVER_ERROR",
        }
        response = Response(
            problem_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content_type="application/problem+json",
        )

    return response
