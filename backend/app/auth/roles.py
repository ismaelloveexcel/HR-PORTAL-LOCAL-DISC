from typing import Any, Iterable, Optional

from fastapi import HTTPException, status

ALLOWED_ROLES = {"admin", "hr", "viewer"}
ROLE_CLAIM_KEYS = ["roles", "role", "groups", "appRoles", "app_roles"]


def _flatten_claim_values(values: Any) -> Iterable[str]:
    if isinstance(values, str):
        return [values]
    if isinstance(values, (list, tuple, set)):
        return [v for v in values if isinstance(v, str)]
    return []


def _map_to_internal_role(value: str) -> Optional[str]:
    normalized = value.lower()
    if "admin" in normalized:
        return "admin"
    if "hr" in normalized or "human" in normalized:
        return "hr"
    if "viewer" in normalized or "read" in normalized:
        return "viewer"
    return None


def resolve_role_from_claims(claims: dict[str, Any]) -> str:
    for key in ROLE_CLAIM_KEYS:
        if key not in claims:
            continue
        for entry in _flatten_claim_values(claims[key]):
            role = _map_to_internal_role(entry)
            if role:
                return role

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No authorized role found in token")
