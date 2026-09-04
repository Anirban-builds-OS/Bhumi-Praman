from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def log_action(
    db: Session,
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    field_name: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    notes: str | None = None,
    commit: bool = True,
) -> AuditLog:
    entry = AuditLog(
        actor_id=actor.id if actor else None,
        actor_name_snapshot=actor.full_name if actor else "system",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        notes=notes,
    )
    db.add(entry)
    if commit:
        db.commit()
        db.refresh(entry)
    return entry
