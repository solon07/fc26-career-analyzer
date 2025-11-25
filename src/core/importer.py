"""
Import pipeline for FC 26 save data.
Processes parser output and inserts into SQLite.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert

from src.database.models import Player, PlayerInfo, Base, engine, SessionLocal
from src.core.parser_bridge import parser_bridge


class NameResolver:
    """
    Resolves player name IDs to actual name strings

    Uses two lookup sources in priority order:
    1. editedplayernames: Names for edited/created players (highest priority)
    2. dcplayernames: Generic name ID lookup (fallback)
    """

    def __init__(self, parsed_data: Dict[str, Any]):
        """
        Initialize name resolver with parser data

        Args:
            parsed_data: Parsed data dictionary (merged)
        """
        self.dcplayernames: Dict[int, str] = {}
        self.editedplayernames: Dict[int, Dict[str, str]] = {}

        print("   Building name lookup tables...")
        self._build_dcplayernames(parsed_data)
        self._build_editedplayernames(parsed_data)

        print(f"   Loaded {len(self.dcplayernames)} generic names")
        print(f"   Loaded {len(self.editedplayernames)} edited player names")

    def _build_dcplayernames(self, parser_data: Dict[str, Any]):
        """Build dcplayernames lookup dict"""
        rows = parser_data.get("dcplayernames", [])
        if not rows:
            print("   Warning: dcplayernames table not found")
            return

        for row in rows:
            nameid = row.get("nameid")
            name = row.get("name")
            if nameid is not None and name:
                self.dcplayernames[nameid] = name

    def _build_editedplayernames(self, parser_data: Dict[str, Any]):
        """Build editedplayernames lookup dict"""
        rows = parser_data.get("editedplayernames", [])
        if not rows:
            print("   Warning: editedplayernames table not found")
            return

        for row in rows:
            playerid = row.get("playerid")
            if playerid is not None:
                self.editedplayernames[playerid] = {
                    "firstname": row.get("firstname", ""),
                    "surname": row.get("surname", ""),
                    "commonname": row.get("commonname", ""),
                    "playerjerseyname": row.get("playerjerseyname", ""),
                }

    def resolve_player_names(
        self,
        playerid: int,
        firstnameid: Optional[int],
        lastnameid: Optional[int],
        commonnameid: Optional[int],
    ) -> Dict[str, str]:
        """
        Resolve all name IDs for a player
        """
        # Check edited names first (highest priority)
        if playerid in self.editedplayernames:
            edited = self.editedplayernames[playerid]
            return {
                "firstname": edited["firstname"] or None,
                "surname": edited["surname"] or None,
                "commonname": edited["commonname"] or None,
            }

        # Fallback to dcplayernames lookup
        return {
            "firstname": self.dcplayernames.get(firstnameid) if firstnameid else None,
            "surname": self.dcplayernames.get(lastnameid) if lastnameid else None,
            "commonname": self.dcplayernames.get(commonnameid)
            if commonnameid
            else None,
        }


class SaveImporter:
    """
    Imports FC 26 save data into SQLite database.
    """

    def __init__(self):
        self.db: Session = None
        self.name_resolver: Optional[NameResolver] = None

    def import_save(self, save_path: str = None) -> Dict[str, int]:
        """
        Complete import pipeline.

        Args:
            save_path: Path to save file (optional)

        Returns:
            Dictionary with import statistics
        """
        print("=" * 60)
        print("FC26 Career Analyzer - Save Import Pipeline")
        print("=" * 60)
        print()

        # Step 1: Initialize database
        print("Step 1: Initializing database...")
        Base.metadata.create_all(bind=engine)
        print("Database ready")
        print()

        # Step 2: Parse save file
        print("Step 2: Parsing save file...")
        try:
            parsed_data = parser_bridge.parse_save(save_path)
        except Exception as e:
            print(f"Failed to parse save: {e}")
            raise
        print()

        # Initialize NameResolver
        print("Step 3: Initializing Name Resolver...")
        self.name_resolver = NameResolver(parsed_data)
        print()

        # Step 4: Import players (merging identity and attributes)
        print("Step 4: Importing players...")
        player_stats = self._import_players(parsed_data)
        print()

        # Step 5: Summary
        print("=" * 60)
        print("IMPORT COMPLETE")
        print("=" * 60)
        print()
        print(
            f"Players imported/updated: {player_stats['players_imported'] + player_stats['players_updated']}"
        )
        print()

        return player_stats

    def _import_players(self, parsed_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Import players merging identity (players) and attributes (career_playergrowthuserseason).

        Args:
            parsed_data: Parsed save data

        Returns:
            Statistics dictionary
        """
        # Get data tables
        players_rows = parsed_data.get("players", [])
        attributes_rows = parsed_data.get("career_playergrowthuserseason", [])

        if not players_rows:
            print("Warning: No player identity data found in save")
            return {"players_imported": 0, "players_updated": 0}

        print(f"   Found {len(players_rows)} players in 'players' table")
        print(
            f"   Found {len(attributes_rows)} players in 'career_playergrowthuserseason' table"
        )

        # Index attributes by playerid for fast lookup
        attributes_map = {
            row["playerid"]: row for row in attributes_rows if "playerid" in row
        }

        # Create session
        db = SessionLocal()

        try:
            imported = 0
            updated = 0

            # We iterate over players_rows as it contains the master list of players
            for player_row in players_rows:
                playerid = player_row.get("playerid")
                if playerid is None:
                    continue

                # Debug first few players
                if imported + updated < 5:
                    print(
                        f"   Processing player {playerid} (Raw ID: {player_row.get('playerid')})"
                    )

                # Get attributes (if any)
                attrs = attributes_map.get(playerid, {})

                # Resolve names
                resolved_names = self.name_resolver.resolve_player_names(
                    playerid=playerid,
                    firstnameid=player_row.get("firstnameid"),
                    lastnameid=player_row.get("lastnameid"),
                    commonnameid=player_row.get("commonnameid"),
                )

                # Determine final names (fallback to Unknown if resolution failed)
                firstname = resolved_names["firstname"] or f"Unknown_{playerid}"
                surname = resolved_names["surname"] or ""
                commonname = resolved_names["commonname"]

                # Map fields to Player model
                player_dict = {
                    "playerid": playerid,
                    "firstname": firstname,
                    "surname": surname,
                    "commonname": commonname,
                    # Attributes (use defaults if missing)
                    "overallrating": attrs.get(
                        "overall", attrs.get("overallrating", 40)
                    ),  # Default to min 40 to satisfy constraint
                    "potential": attrs.get("potential", 40),
                    "age": attrs.get("age", 16),
                    "height": attrs.get("height"),
                    "weight": attrs.get("weight"),
                    "preferredposition1": attrs.get("preferredposition1"),
                    "weakfootabilitytypecode": attrs.get("weakfootabilitytypecode"),
                    "skillmoves": attrs.get("skillmoves"),
                    "value": attrs.get("value"),
                }

                # Ensure constraints are met (simple validation)
                if player_dict["overallrating"] < 40:
                    player_dict["overallrating"] = 40
                if player_dict["potential"] < 40:
                    player_dict["potential"] = 40
                if player_dict["age"] < 16:
                    player_dict["age"] = 16

                # Upsert Player
                stmt = insert(Player).values(**player_dict)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["playerid"], set_=player_dict
                )
                result = db.execute(stmt)

                if result.rowcount > 0:
                    # Check if this was an insert or update
                    # (This check is approximate with on_conflict_do_update)
                    updated += 1  # Assume update/insert happened

                # Also update PlayerInfo for reference (optional but good for debugging)
                info_dict = {
                    "playerid": playerid,
                    "firstname": player_row.get(
                        "firstname"
                    ),  # Original from table (likely None/empty)
                    "surname": player_row.get("surname"),
                    "commonname": player_row.get("commonname"),
                    "nationality": player_row.get("nationality"),
                    "birthdate": player_row.get("birthdate"),
                    # Store IDs too if we added columns for them, but PlayerInfo model
                    # currently has firstname/surname columns which are strings.
                    # The user's PlayerInfo model (from previous steps) had:
                    # firstname, surname, commonname, nationality, birthdate.
                    # It did NOT have firstnameid.
                    # So we can't store IDs there unless we update the model.
                    # For now, let's skip PlayerInfo upsert or just store what we have.
                    # Actually, we should probably store the RESOLVED names in PlayerInfo too if we want to keep it.
                    # But Player model now has the resolved names.
                    # Let's just stick to Player model for now to keep it simple and efficient.
                }

                # If we want to keep PlayerInfo populated:
                info_dict["firstname"] = firstname
                info_dict["surname"] = surname
                info_dict["commonname"] = commonname

                stmt_info = insert(PlayerInfo).values(**info_dict)
                stmt_info = stmt_info.on_conflict_do_update(
                    index_elements=["playerid"], set_=info_dict
                )
                db.execute(stmt_info)

            db.commit()

            print(f"   Processed {len(players_rows)} players")
            # Since we can't easily distinguish insert/update with sqlite upsert without extra query,
            # we'll just report total processed.

            return {"players_imported": len(players_rows), "players_updated": 0}

        except Exception as e:
            db.rollback()
            print(f"   Error importing players: {e}")
            raise
        finally:
            db.close()


# Singleton instance
importer = SaveImporter()
