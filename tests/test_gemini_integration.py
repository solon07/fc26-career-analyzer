"""
End-to-end tests for Gemini integration
Tests the complete query pipeline
"""

import pytest
from src.llm import GeminiClient, PromptBuilder, ContextBuilder
from src.database.models import SessionLocal, Player


class TestGeminiIntegration:
    """Test Gemini integration end-to-end"""

    @pytest.fixture
    def db(self):
        """Database session fixture"""
        session = SessionLocal()
        yield session
        session.close()

    @pytest.fixture
    def client(self):
        """Gemini client fixture"""
        try:
            return GeminiClient()
        except ValueError:
            pytest.skip("GEMINI_API_KEY not configured")

    @pytest.fixture
    def builder(self, db):
        """Context builder fixture"""
        return ContextBuilder(db)

    def test_client_initialization(self, client):
        """Test that Gemini client initializes"""
        assert client is not None
        assert client.model is not None

    def test_context_building(self, builder):
        """Test context builder creates valid context"""
        context = builder.build_summary_context()
        assert context is not None
        assert len(context) > 0
        assert "jogadores" in context.lower() or "player" in context.lower()

    def test_prompt_building(self):
        """Test prompt builder creates valid prompts"""
        prompt, system = PromptBuilder.build_prompt(
            query="Quem são os melhores jogadores?",
            context="Player A: OVR 85\nPlayer B: OVR 80",
            query_type="player_query",
        )

        assert prompt is not None
        assert "Player A" in prompt
        assert system is not None
        assert "FC26" in system

    @pytest.mark.integration
    def test_simple_query(self, client, builder):
        """Test a simple query end-to-end"""
        # Build context
        context = builder.build_top_players_context(top_n=5)

        # Build prompt
        prompt, system = PromptBuilder.build_prompt(
            query="Liste os 3 melhores jogadores",
            context=context,
            query_type="player_query",
        )

        # Query Gemini
        response = client.query(prompt, system)

        # Assertions
        assert response["success"] == True
        assert len(response["text"]) > 0
        assert response["tokens_used"] > 0

    @pytest.mark.integration
    def test_comparison_query(self, client, builder):
        """Test a comparison query"""
        context = builder.build_player_context(limit=10)

        prompt, system = PromptBuilder.build_prompt(
            query="Compare os dois melhores jogadores",
            context=context,
            query_type="comparison",
        )

        response = client.query(prompt, system)

        assert response["success"] == True
        assert len(response["text"]) > 50  # Should be detailed

    @pytest.mark.integration
    def test_statistics_query(self, client, builder):
        """Test a statistics query"""
        context = builder.build_summary_context()

        prompt, system = PromptBuilder.build_prompt(
            query="Qual o overall médio do elenco?",
            context=context,
            query_type="statistics",
        )

        response = client.query(prompt, system)

        assert response["success"] == True
        # Should contain numbers
        assert any(char.isdigit() for char in response["text"])
