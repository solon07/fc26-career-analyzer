"""
Query Router - Intelligent routing between SQL and Gemini
Analyzes queries and chooses the most efficient execution path
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import func
import re

from src.database.models import Player
from .gemini_client import GeminiClient
from .prompt_builder import PromptBuilder
from .context_builder import ContextBuilder


class QueryType(Enum):
    """Types of queries we can handle"""

    SIMPLE_COUNT = "simple_count"  # "Quantos jogadores tenho?"
    SIMPLE_TOP_N = "simple_top_n"  # "Top 5 jogadores"
    SIMPLE_FILTER = "simple_filter"  # "Jogadores com OVR > 80"
    COMPLEX_REASONING = "complex"  # Needs Gemini reasoning
    COMPARISON = "comparison"  # Compare players
    RECOMMENDATION = "recommendation"  # "Quem devo contratar?"


class QueryRouter:
    """
    Routes queries to SQL or Gemini based on complexity

    Decision logic:
    - Simple queries (counts, filters, top-N) → SQL (fast, free)
    - Complex queries (reasoning, recommendations) → Gemini (smart, costs tokens)
    """

    def __init__(self, db: Session, gemini_client: GeminiClient):
        self.db = db
        self.gemini_client = gemini_client
        self.context_builder = ContextBuilder(db)

    def route_query(self, question: str) -> Dict[str, Any]:
        """
        Main routing method

        Returns:
            {
                'answer': str,
                'source': 'sql' | 'gemini',
                'query_type': QueryType,
                'tokens_used': int,
                'success': bool
            }
        """
        # Classify query
        query_type = self._classify_query(question)

        # Route based on type
        if query_type in [
            QueryType.SIMPLE_COUNT,
            QueryType.SIMPLE_TOP_N,
            QueryType.SIMPLE_FILTER,
        ]:
            return self._handle_sql_query(question, query_type)
        else:
            return self._handle_gemini_query(question, query_type)

    def _classify_query(self, question: str) -> QueryType:
        """Classify query type using simple heuristics"""
        q = question.lower()

        # Simple count
        if any(word in q for word in ["quantos", "quantidade", "total de"]):
            return QueryType.SIMPLE_COUNT

        # Top N
        if any(
            word in q for word in ["top", "melhores", "piores", "maiores", "menores"]
        ):
            # Check if it's just a simple ranking
            if (
                any(word in q for word in ["5", "10", "cinco", "dez"])
                and "jogadores" in q
            ):
                return QueryType.SIMPLE_TOP_N

        # Comparison
        if any(
            word in q for word in ["comparar", "compare", "diferença", "vs", "versus"]
        ):
            return QueryType.COMPARISON

        # Recommendation
        if any(
            word in q
            for word in ["devo", "deveria", "recomend", "suger", "melhor para"]
        ):
            return QueryType.RECOMMENDATION

        # Default to complex (use Gemini)
        return QueryType.COMPLEX_REASONING

    def _handle_sql_query(self, question: str, query_type: QueryType) -> Dict[str, Any]:
        """Handle queries that can be answered with SQL"""
        try:
            if query_type == QueryType.SIMPLE_COUNT:
                count = self.db.query(Player).count()
                answer = f"Você tem **{count} jogadores** no seu elenco."

            elif query_type == QueryType.SIMPLE_TOP_N:
                # Extract number (default 10)
                numbers = re.findall(r"\d+", question)
                top_n = int(numbers[0]) if numbers else 10
                top_n = min(top_n, 50)  # Cap at 50

                players = (
                    self.db.query(Player)
                    .filter(Player.overallrating.isnot(None))
                    .order_by(Player.overallrating.desc())
                    .limit(top_n)
                    .all()
                )

                answer = f"**Top {top_n} Jogadores por Overall:**\n\n"
                for i, p in enumerate(players, 1):
                    answer += f"{i}. {p.detailed_display}\n"

            elif query_type == QueryType.SIMPLE_FILTER:
                # Fallback to Gemini for now (complex filtering)
                return self._handle_gemini_query(question, query_type)

            else:
                return self._handle_gemini_query(question, query_type)

            return {
                "answer": answer,
                "source": "sql",
                "query_type": query_type.value,
                "tokens_used": 0,
                "success": True,
            }

        except Exception as e:
            # Fallback to Gemini on SQL error
            return self._handle_gemini_query(question, QueryType.COMPLEX_REASONING)

    def _handle_gemini_query(
        self, question: str, query_type: QueryType
    ) -> Dict[str, Any]:
        """Handle queries that need Gemini reasoning"""
        try:
            # Build appropriate context
            if query_type == QueryType.SIMPLE_TOP_N:
                context = self.context_builder.build_top_players_context(top_n=20)
            elif query_type == QueryType.COMPARISON:
                context = self.context_builder.build_player_context(limit=50)
            elif query_type in [QueryType.RECOMMENDATION, QueryType.COMPLEX_REASONING]:
                context = self.context_builder.build_player_context(limit=30)
            else:
                context = self.context_builder.build_summary_context()

            # Build prompt
            prompt_type = {
                QueryType.COMPARISON: "comparison",
                QueryType.SIMPLE_TOP_N: "player_query",
                QueryType.RECOMMENDATION: "general",
                QueryType.COMPLEX_REASONING: "general",
            }.get(query_type, "general")

            prompt, system = PromptBuilder.build_prompt(
                query=question, context=context, query_type=prompt_type
            )

            # Query Gemini
            response = self.gemini_client.query(prompt, system)

            if response["success"]:
                return {
                    "answer": response["text"],
                    "source": "gemini",
                    "query_type": query_type.value,
                    "tokens_used": response["tokens_used"],
                    "success": True,
                }
            else:
                return {
                    "answer": f"Erro ao consultar Gemini: {response['error']}",
                    "source": "error",
                    "query_type": query_type.value,
                    "tokens_used": 0,
                    "success": False,
                }

        except Exception as e:
            return {
                "answer": f"Erro inesperado: {str(e)}",
                "source": "error",
                "query_type": query_type.value,
                "tokens_used": 0,
                "success": False,
            }
