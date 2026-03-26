from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Index

from app.core.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index = True, nullable=False)

    token_hash: Mapped[str]= mapped_column(String(255), unique= True, index= True, nullable=False)

    revoked: Mapped[bool] = mapped_column(Boolean, default = False, nullable= False)

    #rotation support - invalidate refresh token and issue a new one after each use
    replaced_by_hash : Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), nullable = False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable = False)

Index("ix_refresh_tokens_user_revoked", RefreshToken.user_id, RefreshToken.revoked)