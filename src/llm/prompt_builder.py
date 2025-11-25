"""
Prompt template system
Builds structured prompts for Gemini queries
"""

from typing import Optional, List, Dict, Any


class PromptBuilder:
    """
    Builds prompts for Gemini using templates

    Templates include:
    - System instructions (role, capabilities, constraints)
    - Context injection (database data)
    - User query formatting
    """

    # System instruction template
    SYSTEM_INSTRUCTION = """You are a FC26 Career Mode Analyzer AI assistant.

Your role:
- Analyze EA Sports FC 26 Career Mode save data
- Answer questions about players, teams, matches, and statistics
- Provide insights based on the provided context
- Respond in Portuguese (Brazilian)

Your capabilities:
- Access to player stats, contracts, match history, growth records
- Can compare players, analyze trends, identify patterns
- Understand soccer/football terminology

Your constraints:
- ONLY use information provided in the context
- If data is not in context, say "Não tenho esses dados no momento"
- Be concise but informative
- Use markdown formatting for readability
- When players appear as "Player #ID", acknowledge this limitation naturally

Response format:
- Direct answer first
- Supporting data/evidence
- Additional insights if relevant
- Markdown tables for comparisons"""

    # Query templates by type
    TEMPLATES = {
        "player_query": """Context about players:
{context}

User question: {query}

Answer in Portuguese, using the context above:""",
        "comparison": """Context for comparison:
{context}

User wants to compare: {query}

Provide a detailed comparison in Portuguese with a markdown table:""",
        "statistics": """Statistical data:
{context}

User asks: {query}

Analyze and respond in Portuguese with key statistics:""",
        "general": """Career save data:
{context}

User question: {query}

Answer in Portuguese based on the data provided:""",
    }

    @classmethod
    def build_prompt(
        cls,
        query: str,
        context: str,
        query_type: str = "general",
        include_system: bool = True,
    ) -> tuple[str, Optional[str]]:
        """
        Build a complete prompt

        Args:
            query: User's question
            context: Data context from database
            query_type: Type of query (player_query, comparison, etc.)
            include_system: Include system instruction

        Returns:
            Tuple of (prompt, system_instruction)
        """
        # Get template
        template = cls.TEMPLATES.get(query_type, cls.TEMPLATES["general"])

        # Build prompt
        prompt = template.format(context=context, query=query)

        # System instruction (optional)
        system_instruction = cls.SYSTEM_INSTRUCTION if include_system else None

        return prompt, system_instruction

    @classmethod
    def build_simple_prompt(cls, query: str, context: str) -> str:
        """Build a simple prompt without templates"""
        return f"""Context: {context}

Question: {query}

Answer in Portuguese:"""

    @classmethod
    def format_player_context(cls, players: List[Dict[str, Any]]) -> str:
        """Format player data for context"""
        if not players:
            return "Nenhum jogador encontrado."

        lines = []
        for p in players:
            line = (
                f"- {p.get('name', 'Player #' + str(p['id']))}: "
                f"OVR {p.get('overall', '?')}, "
                f"{p.get('position', '?')}, "
                f"Age {p.get('age', '?')}"
            )
            lines.append(line)

        return "\n".join(lines)
