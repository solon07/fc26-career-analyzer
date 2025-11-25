"""
Context builder
Converts database data into LLM-friendly context strings
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.database.models import Player, PlayerInfo


class ContextBuilder:
    """
    Builds context strings from database data

    Handles:
    - Player data formatting
    - Token limit management
    - Relevance filtering
    """

    def __init__(self, db: Session, max_tokens: int = 4000):
        """
        Initialize context builder

        Args:
            db: Database session
            max_tokens: Max tokens for context (leaves room for response)
        """
        self.db = db
        self.max_tokens = max_tokens

    def build_player_context(
        self,
        player_ids: Optional[List[int]] = None,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build context from player data

        Args:
            player_ids: Specific player IDs to include
            limit: Max players to include
            filters: SQLAlchemy filters (e.g., {'overallrating__gte': 80})

        Returns:
            Formatted context string
        """
        # Base query
        query = self.db.query(Player)

        # Apply filters
        if player_ids:
            query = query.filter(Player.playerid.in_(player_ids))

        if filters:
            for key, value in filters.items():
                if "__" in key:
                    field, op = key.split("__")
                    column = getattr(Player, field)

                    if op == "gte":
                        query = query.filter(column >= value)
                    elif op == "lte":
                        query = query.filter(column <= value)
                    elif op == "eq":
                        query = query.filter(column == value)

        # Get players
        players = query.limit(limit).all()

        if not players:
            return "⚠️ Nenhum jogador encontrado com os critérios especificados."

        # Format context
        lines = [f"📊 Total de jogadores: {len(players)}\n"]

        for player in players:
            line = (
                f"• {player.detailed_display}\n"
                f"  ID: {player.playerid}, "
                f"Age: {player.age or '?'}, "
                f"Potential: {player.potential or '?'}"
            )
            lines.append(line)

        context = "\n".join(lines)

        # Check token limit (rough estimate)
        if len(context) > self.max_tokens * 4:  # 1 token ≈ 4 chars
            # Truncate if needed
            truncated = context[: self.max_tokens * 4]
            context = truncated + "\n\n⚠️ [Context truncated due to size]"

        return context

    def build_top_players_context(
        self, top_n: int = 10, order_by: str = "overallrating"
    ) -> str:
        """Build context with top N players"""
        column = getattr(Player, order_by)
        players = (
            self.db.query(Player)
            .filter(column.isnot(None))
            .order_by(column.desc())
            .limit(top_n)
            .all()
        )

        if not players:
            return "⚠️ Nenhum jogador encontrado."

        lines = [f"🏆 Top {top_n} jogadores por {order_by}:\n"]

        for i, player in enumerate(players, 1):
            lines.append(f"{i}. {player.detailed_display}")

        return "\n".join(lines)

    def build_summary_context(self) -> str:
        """Build a summary context of the career save"""
        total_players = self.db.query(Player).count()

        if total_players == 0:
            return "⚠️ Nenhum dado carregado."

        # Get top player
        top_player = (
            self.db.query(Player)
            .filter(Player.overallrating.isnot(None))
            .order_by(Player.overallrating.desc())
            .first()
        )

        # Average stats
        from sqlalchemy import func

        avg_ovr = self.db.query(func.avg(Player.overallrating)).scalar() or 0
        avg_age = self.db.query(func.avg(Player.age)).scalar() or 0

        summary = f"""📊 Resumo da Carreira:
- Total de jogadores: {total_players}
- Overall médio: {avg_ovr:.1f}
- Idade média: {avg_age:.1f} anos
- Melhor jogador: {top_player.detailed_display if top_player else 'N/A'}
"""
        return summary
