"""
Signed, stateless task tokens.

A task token encodes everything the server needs to score an answer
(kind, side identities, control flag, expected winner) so that
``next_set`` and ``answer`` can run on different workers and the client
cannot see which tasks are controls.
"""
from __future__ import annotations

from typing import Any

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

_SALT = "jugglefit.rating.task"
_TTL_SECONDS = 60 * 60  # tokens valid for 1 hour


def _serializer() -> URLSafeTimedSerializer:
    # Use the Flask app's SECRET_KEY so there's a single source of truth
    # and no hardcoded fallback secret in this module.
    return URLSafeTimedSerializer(current_app.secret_key, salt=_SALT)


def sign(payload: dict[str, Any]) -> str:
    return _serializer().dumps(payload)


def unsign(token: str) -> dict[str, Any]:
    try:
        return _serializer().loads(token, max_age=_TTL_SECONDS)
    except SignatureExpired as e:
        raise ValueError("task expired") from e
    except BadSignature as e:
        raise ValueError("invalid task") from e
