import os
import secrets

from fastapi import Header, HTTPException, status


def verify_api_token(
    authorization: str | None = Header(default=None)
):
    expected_token = os.getenv("BACKEND_API_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured"
        )

    scheme, _, token = (authorization or "").partition(" ")

    if (
        scheme.lower() != "bearer"
        or not token
        or not secrets.compare_digest(token, expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"}
        )