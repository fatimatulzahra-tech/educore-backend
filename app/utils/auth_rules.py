SPECIAL_ROLES = ["platform_admin", "principal"]

def requires_password_flow(role: str) -> bool:
    return role not in SPECIAL_ROLES