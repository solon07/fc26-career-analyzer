"""
PlayerInfo model representing the players table.
Contains identity information (names, nationality, etc).
"""

from sqlalchemy import Column, Integer, String
from .base import Base


class PlayerInfo(Base):
    """
    Represents player identity information from the 'players' table.
    This is separate from Player (career_playergrowthuserseason) which contains attributes.
    """

    __tablename__ = "player_info"

    # Primary Key
    playerid = Column(Integer, primary_key=True, index=True)

    # Identity Information
    firstname = Column(String(50), nullable=True, index=True)
    surname = Column(String(50), nullable=True, index=True)
    commonname = Column(String(50), nullable=True)

    # Additional Info (optional, add if present in parser output)
    nationality = Column(Integer, nullable=True)
    birthdate = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<PlayerInfo {self.firstname} {self.surname} (ID: {self.playerid})>"
