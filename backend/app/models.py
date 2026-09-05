from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


# ============================================================
# USER PROFILE MODEL
# ============================================================

class UserProfile(Base):

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    preferred_role: Mapped[str] = mapped_column(
        String(100)
    )

    location: Mapped[str] = mapped_column(
        String(100)
    )

    experience: Mapped[str] = mapped_column(
        String(50)
    )

    skills: Mapped[str] = mapped_column(
        Text
    )

    expected_salary: Mapped[str] = mapped_column(
        String(50)
    )