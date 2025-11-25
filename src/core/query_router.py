"""
Query Router - Decide se usa SQL direto ou Gemini.
"""

from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..database.models import Player
import re


class QueryRouter:
    """Route queries to SQL or Gemini based on complexity."""

    # Patterns para queries SQL
    SQL_PATTERNS = [
        # Estatísticas simples
        (r"quantos jogadores", "count_players"),
        (r"total de jogadores", "count_players"),
        (r"número de jogadores", "count_players"),
        # Rating queries
        (r"melhor jogador", "top_players"),
        (r"melhores jogadores", "top_players"),
        (r"top \d+ jogadores", "top_players"),
        (r"jogadores acima de (\d+)", "rating_above"),
        # Age queries
        (r"jogadores jovens", "young_players"),
        (r"jogadores com menos de (\d+) anos", "age_below"),
        (r"jogadores mais velhos", "old_players"),
        # Potential
        (r"alto potencial", "high_potential"),
        (r"potencial acima de (\d+)", "potential_above"),
        # Specific player
        (r"informações sobre (\w+)", "player_info"),
        (r"dados do (\w+)", "player_info"),
    ]

    def __init__(self, db: Session):
        self.db = db

    def route(self, query: str) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        """
        Route a query to SQL or Gemini.

        Returns:
            Tuple[source, sql_result, query_for_gemini]
            - source: "sql" or "gemini"
            - sql_result: Result if SQL was used, None otherwise
            - query_for_gemini: Original query if Gemini needed, None if SQL handled it
        """
        query_lower = query.lower().strip()

        # Try to match SQL patterns
        for pattern, handler_name in self.SQL_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                # Execute SQL handler
                handler = getattr(self, f"_handle_{handler_name}", None)
                if handler:
                    try:
                        result = handler(match, query_lower)
                        if result:
                            return ("sql", result, None)
                    except Exception:
                        # SQL failed, fallback to Gemini
                        pass

        # Complex query - use Gemini
        return ("gemini", None, query)

    # SQL Handlers
    def _handle_count_players(self, match, query: str) -> str:
        count = self.db.query(Player).count()
        return f"Há **{count} jogadores** no seu save."

    def _handle_top_players(self, match, query: str) -> str:
        # Extract number if "top N"
        top_match = re.search(r"top (\d+)", query)
        limit = int(top_match.group(1)) if top_match else 5

        players = (
            self.db.query(Player)
            .order_by(Player.overallrating.desc())
            .limit(limit)
            .all()
        )

        result = f"**Top {limit} Jogadores:**\n\n"
        for i, p in enumerate(players, 1):
            result += f"{i}. {p.display_name} - OVR {p.overallrating} ({p.preferredposition1 or 'N/A'})\n"

        return result

    def _handle_rating_above(self, match, query: str) -> str:
        threshold = int(match.group(1))
        players = (
            self.db.query(Player)
            .filter(Player.overallrating >= threshold)
            .order_by(Player.overallrating.desc())
            .all()
        )

        result = (
            f"**Jogadores com OVR ≥ {threshold}:** ({len(players)} encontrados)\n\n"
        )
        for p in players[:10]:  # Limitar a 10
            result += f"- {p.display_name}: OVR {p.overallrating}\n"

        if len(players) > 10:
            result += f"\n_... e mais {len(players) - 10} jogadores_"

        return result

    def _handle_young_players(self, match, query: str) -> str:
        players = (
            self.db.query(Player)
            .filter(Player.age <= 21)
            .order_by(Player.potential.desc())
            .limit(10)
            .all()
        )

        result = "**Jogadores Jovens (≤21 anos) com Alto Potencial:**\n\n"
        for p in players:
            growth = p.potential - p.overallrating if p.potential else 0
            result += f"- {p.display_name} ({p.age} anos): OVR {p.overallrating} → POT {p.potential} (+{growth})\n"

        return result

    def _handle_age_below(self, match, query: str) -> str:
        max_age = int(match.group(1))
        count = self.db.query(Player).filter(Player.age < max_age).count()
        return f"Há **{count} jogadores** com menos de {max_age} anos."

    def _handle_old_players(self, match, query: str) -> str:
        players = (
            self.db.query(Player)
            .filter(Player.age >= 35)
            .order_by(Player.age.desc())
            .limit(10)
            .all()
        )

        result = "**Jogadores Veteranos (≥35 anos):**\n\n"
        for p in players:
            result += f"- {p.display_name}: {p.age} anos, OVR {p.overallrating}\n"

        return result if players else "Nenhum jogador com 35+ anos encontrado."

    def _handle_high_potential(self, match, query: str) -> str:
        players = (
            self.db.query(Player)
            .filter(Player.potential >= 85)
            .order_by(Player.potential.desc())
            .limit(10)
            .all()
        )

        result = "**Jogadores com Alto Potencial (≥85):**\n\n"
        for p in players:
            growth = p.potential - p.overallrating
            result += f"- {p.display_name}: OVR {p.overallrating} → POT {p.potential} (+{growth})\n"

        return result

    def _handle_potential_above(self, match, query: str) -> str:
        threshold = int(match.group(1))
        count = self.db.query(Player).filter(Player.potential >= threshold).count()
        return f"Há **{count} jogadores** com potencial ≥ {threshold}."

    def _handle_player_info(self, match, query: str) -> str:
        # Buscar jogador por nome (parcial)
        name = match.group(1)
        player = (
            self.db.query(Player).filter(Player.display_name.ilike(f"%{name}%")).first()
        )

        if not player:
            return None  # Fallback to Gemini

        return player.detailed_display()
