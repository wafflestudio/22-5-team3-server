from __future__ import annotations
from typing import List, Optional

from sqlalchemy import BigInteger, String, ForeignKey, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from snuvote.database.common import Base

from datetime import datetime


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    userid: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(20))
    college: Mapped[int] = mapped_column(Integer)

    votes: Mapped[Optional[List["Vote"]]] = relationship("Vote", back_populates="writer")

    choice_participations: Mapped[Optional[List["ChoiceParticipation"]]] = relationship("ChoiceParticipation", back_populates="user")

    comments: Mapped[Optional[List["Comment"]]] = relationship("Comment", back_populates="writer")

class Vote(Base):
    __tablename__ = "vote"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    writer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    writer: Mapped["User"] = relationship("User", back_populates="votes")
    
    create_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    participation_code_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    participation_code: Mapped[str] = mapped_column(String(20), nullable=True)
    realtime_result: Mapped[bool] = mapped_column(Boolean, nullable=False)
    multiple_choice: Mapped[bool] = mapped_column(Boolean, nullable=False)
    annonymous_choice: Mapped[bool] = mapped_column(Boolean, nullable=False)

    choices: Mapped[Optional[List["Choice"]]] = relationship("Choice", back_populates="vote", uselist=True)
    
    comments: Mapped[Optional[List["Comment"]]] = relationship("Comment", back_populates="vote", uselist=True)

class Choice(Base):
    __tablename__ = "choice"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    vote_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vote.id"))
    vote: Mapped["Vote"] = relationship("Vote", back_populates="choices", uselist=False)

    choice_content: Mapped[str] = mapped_column(String(100), nullable=False)

    choice_participations: Mapped[Optional[List["ChoiceParticipation"]]] = relationship("ChoiceParticipation", back_populates="choice")

class ChoiceParticipation(Base):
    __tablename__ = "choice_participation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User", back_populates="choice_participations", uselist=False)

    choice_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("choice.id"))
    choice: Mapped["Choice"] = relationship("Choice", uselist=False)

class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    vote_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vote.id"))
    vote: Mapped["Vote"] = relationship("Vote", back_populates="comments", uselist=False)

    writer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    writer: Mapped["User"] = relationship("User", back_populates="comments", uselist=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    create_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    edited_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class BlockedRefreshToken(Base):
    __tablename__ = "blocked_refresh_token"

    token_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)