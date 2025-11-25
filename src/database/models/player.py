"""
Player model representing career_playergrowthuserseason table.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import validates, relationship
from .base import Base


class Player(Base):
    """
    Represents a player in the user's squad.
    Maps to career_playergrowthuserseason table from FC 26 save.
    """

    __tablename__ = "players"

    # Primary Key
    playerid = Column(Integer, primary_key=True, index=True)

    # Personal Information
    firstname = Column(String(50), nullable=False, index=True)
    surname = Column(String(50), nullable=False, index=True)
    commonname = Column(String(50), nullable=True)

    # Ratings (40-99 range)
    overallrating = Column(Integer, nullable=False, index=True)
    potential = Column(Integer, nullable=True)

    # Physical Attributes
    age = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)  # in cm
    weight = Column(Integer, nullable=True)  # in kg

    # Position and Skills
    preferredposition1 = Column(String(10), nullable=True)
    weakfootabilitytypecode = Column(Integer, nullable=True)  # 1-5
    skillmoves = Column(Integer, nullable=True)  # 1-5

    # Value and Contract
    value = Column(Integer, nullable=True)  # in currency units

    # Relationship to PlayerInfo (names)
    info = relationship(
        "PlayerInfo",
        foreign_keys="Player.playerid",
        primaryjoin="Player.playerid == PlayerInfo.playerid",
        uselist=False,
        lazy="joined",  # Always load names with player
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "overallrating >= 40 AND overallrating <= 99", name="check_overall_range"
        ),
        CheckConstraint(
            "potential >= 40 AND potential <= 99", name="check_potential_range"
        ),
        CheckConstraint("age >= 16 AND age <= 50", name="check_age_range"),
        CheckConstraint(
            "weakfootabilitytypecode >= 1 AND weakfootabilitytypecode <= 5",
            name="check_weakfoot_range",
        ),
        CheckConstraint(
            "skillmoves >= 1 AND skillmoves <= 5", name="check_skillmoves_range"
        ),
    )

    # Validators
    @validates("overallrating")
    def validate_overall(self, key, value):
        if value is not None and (value < 40 or value > 99):
            raise ValueError(f"Overall rating must be between 40-99, got {value}")
        return value

    @validates("potential")
    def validate_potential(self, key, value):
        if value is not None and (value < 40 or value > 99):
            raise ValueError(f"Potential must be between 40-99, got {value}")
        return value

    @validates("age")
    def validate_age(self, key, value):
        if value is not None and (value < 16 or value > 50):
            raise ValueError(f"Age must be between 16-50, got {value}")
        return value

    # Properties
    @property
    def full_name(self):
        """Returns the player's full name from PlayerInfo table."""
        if self.info:
            if self.info.commonname:
                return self.info.commonname
            return f"{self.info.firstname} {self.info.surname}".strip()
        return f"Player {self.playerid}"  # Fallback if no info

    @property
    def growth_potential(self):
        """Returns the potential for growth (potential - current overall)."""
        if self.potential and self.overallrating:
            return self.potential - self.overallrating
        return 0

    @property
    def display_name(self) -> str:
        """
        User-friendly display name
        Returns actual name if available, formatted ID if not
        """
        # Check if we have a valid name that isn't an "Unknown_" placeholder
        if self.firstname and not self.firstname.startswith("Unknown_"):
            return self.full_name
        return f"Player #{self.playerid}"

    @property
    def detailed_display(self) -> str:
        """
        Detailed display with key stats
        Example: "Player #71055 (OVR 85, ST)"
        """
        name = self.display_name
        ovr = f"OVR {self.overallrating}" if self.overallrating else "OVR ?"
        pos = self.preferredposition1 or "?"
        return f"{name} ({ovr}, {pos})"

    def __repr__(self):
        return f"<Player {self.detailed_display}>"
