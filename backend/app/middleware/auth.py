from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, UserRole
from app.services.auth_service import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolves the authenticated user strictly from the verified JWT's
    subject claim, never from anything the client sends in the request body
    -- role is always looked up server-side from the user row, not accepted
    from the client (see spec's login-page audit note: the UI may offer
    quick demo-account shortcuts, but authorization itself never trusts the
    client's say-so about its own privilege level)."""
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def require_roles(*roles: UserRole):
    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to perform this action")
        return user
    return _check


require_administrator = require_roles(UserRole.ADMINISTRATOR)
require_verifier = require_roles(UserRole.ADMINISTRATOR, UserRole.VERIFICATION_OFFICER)
require_any_role = require_roles(UserRole.ADMINISTRATOR, UserRole.VERIFICATION_OFFICER, UserRole.RECORD_OFFICER)
