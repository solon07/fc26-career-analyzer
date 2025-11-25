"""
Integration tests for LLM module.
"""

import pytest
import os
from unittest.mock import Mock, patch
from llm import GeminiClient, PromptBuilder, ContextBuilder
from database.models import Player


class TestGeminiClient:
    """Test Gemini API integration."""

    def test_client_initialization(self):
        """Test client can be initialized with API key."""
        client = GeminiClient("fake-api-key")
        assert client.api_key == "fake-api-key"

    @patch.dict(os.environ, {}, clear=True)
    def test_client_requires_api_key(self):
        """Test client raises error without API key."""
        with pytest.raises(ValueError):
            GeminiClient(None)

    @patch("google.generativeai.GenerativeModel")
    def test_generate_success(self, mock_model):
        """Test successful generation."""
        # Mock response
        mock_response = Mock()
        mock_response.text = "Test response from Gemini"
        mock_model.return_value.generate_content.return_value = mock_response

        client = GeminiClient("fake-key")
        result = client.query("Test prompt")

        assert result["text"] == "Test response from Gemini"
        assert result["success"] is True
        mock_model.return_value.generate_content.assert_called_once()

    @patch("google.generativeai.GenerativeModel")
    def test_generate_handles_errors(self, mock_model):
        """Test error handling in generation."""
        mock_model.return_value.generate_content.side_effect = Exception("API Error")

        client = GeminiClient("fake-key")
        result = client.query("Test prompt")

        assert result["success"] is False
        assert "API Error" in result["error"]


class TestPromptBuilder:
    """Test prompt construction."""

    def test_build_prompt(self):
        """Test query prompt construction."""
        context = "Player: Test Player, OVR: 85"

        prompt, system = PromptBuilder.build_prompt("Who is the best?", context)

        assert "Who is the best?" in prompt
        assert "Test Player" in prompt
        assert "85" in prompt
        assert system is not None
        assert "FC26 Career Mode Analyzer" in system

    def test_simple_prompt(self):
        """Test simple prompt construction."""
        context = "Total players: 5"

        prompt = PromptBuilder.build_simple_prompt("Test question", context)

        assert "Total players: 5" in prompt
        assert "Test question" in prompt


class TestContextBuilder:
    """Test context building for LLM."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()

        # Mock players
        mock_player = Mock(spec=Player)
        mock_player.playerid = 1
        mock_player.firstname = "Test"
        mock_player.surname = "Player"
        mock_player.commonname = "Test Player"
        mock_player.overallrating = 85
        mock_player.potential = 90
        mock_player.age = 22
        mock_player.preferredposition1 = "ST"

        # Mock detailed_display property
        mock_player.detailed_display = "Test Player (OVR 85, ST)"

        # Setup mock chain: db.query().filter().order_by().limit().all()
        query_mock = db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_by_mock = filter_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = [mock_player]

        # Also setup for simple query: db.query().limit().all()
        query_mock.limit.return_value.all.return_value = [mock_player]

        # Count
        query_mock.count.return_value = 1

        # First (for summary)
        order_by_mock.first.return_value = mock_player

        # Scalar (for avg)
        query_mock.scalar.return_value = 85.0

        return db

    def test_build_summary_context(self, mock_db):
        """Test summary context building."""
        builder = ContextBuilder(mock_db)
        context = builder.build_context("summary", limit=10)

        assert "Resumo da Carreira" in context
        assert "Total de jogadores: 1" in context
        assert "Overall médio" in context

    def test_build_top_players_context(self, mock_db):
        """Test top players context."""
        builder = ContextBuilder(mock_db)
        context = builder.build_context("top_players", limit=5)

        assert "Top 5 jogadores" in context
        assert "Test Player" in context
        assert "OVR 85" in context

    def test_context_includes_player_details(self, mock_db):
        """Test that context includes necessary player details."""
        builder = ContextBuilder(mock_db)
        context = builder.build_context("top_players", limit=1)

        assert "Test Player" in context
        assert "85" in context


class TestEndToEndQuery:
    """End-to-end test of query pipeline."""

    @pytest.mark.integration
    @patch("llm.gemini_client.genai.GenerativeModel")
    def test_full_query_pipeline(self, mock_model, test_db_with_players):
        """Test complete query flow from CLI to response."""
        # Setup
        mock_response = Mock()
        mock_response.text = "Your best player is Test Player with 85 OVR."
        mock_model.return_value.generate_content.return_value = mock_response

        # Build context
        builder = ContextBuilder(test_db_with_players)
        context = builder.build_context("top_players", limit=5)

        # Build prompt
        prompt, system = PromptBuilder.build_prompt("Who is my best player?", context)

        # Generate response
        client = GeminiClient("fake-key")
        result = client.query(prompt, system_instruction=system)

        # Assertions
        assert "Test Player" in result["text"]
        assert "85" in result["text"]


@pytest.fixture
def test_db_with_players(db_session):
    """Fixture that provides DB with test players."""
    from database.models import Player

    players = [
        Player(
            playerid=1,
            firstname="Cristiano",
            surname="Ronaldo",
            commonname="Cristiano Ronaldo",
            overallrating=89,
            potential=89,
            age=39,
            preferredposition1="ST",
        ),
        Player(
            playerid=2,
            firstname="Kylian",
            surname="Mbappé",
            commonname="Kylian Mbappé",
            overallrating=92,
            potential=95,
            age=25,
            preferredposition1="LW",
        ),
    ]

    for player in players:
        db_session.add(player)
    db_session.commit()

    return db_session
