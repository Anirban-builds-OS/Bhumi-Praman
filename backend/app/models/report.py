from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    land_record_id: Mapped[int] = mapped_column(ForeignKey("land_records.id"))
    generated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    file_path: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    land_record: Mapped["LandRecord"] = relationship()  # noqa: F821
    generated_by: Mapped["User"] = relationship()  # noqa: F821
