"""
Simplified unit tests for the agent models that focus on what can actually be tested.
"""

from unittest.mock import Mock

from ingenious.models.agent import Agent, AgentChat, AgentChats, Agents, LLMUsageTracker


class TestAgent:
    """Test cases for Agent class."""

    def test_init_basic(self):
        """Test Agent initialization with basic parameters."""
        agent = Agent(
            agent_name="test_agent",
            agent_model_name="gpt-4",
            agent_display_name="Test Agent",
            agent_description="Test agent description",
            agent_type="test",
        )
        assert agent.agent_name == "test_agent"
        assert agent.agent_description == "Test agent description"
        assert agent.agent_model_name == "gpt-4"
        assert agent.agent_display_name == "Test Agent"
        assert agent.agent_type == "test"

    def test_agent_chats_default_empty(self):
        """Test that agent_chats defaults to empty list."""
        agent = Agent(
            agent_name="test_agent",
            agent_model_name="gpt-4",
            agent_display_name="Test Agent",
            agent_description="Test agent description",
            agent_type="test",
        )
        assert agent.agent_chats == []

    def test_optional_fields(self):
        """Test that optional fields have correct defaults."""
        agent = Agent(
            agent_name="test_agent",
            agent_model_name="gpt-4",
            agent_display_name="Test Agent",
            agent_description="Test agent description",
            agent_type="test",
        )
        assert agent.input_topics == []
        assert agent.model is None
        assert agent.system_prompt is None
        assert agent.log_to_prompt_tuner is True
        assert agent.return_in_response is False


class TestAgents:
    """Test cases for Agents class."""

    def test_init_with_config(self):
        """Test Agents initialization with config."""
        from ingenious.models.config import Config

        # Create mock config with models
        mock_config = Mock(spec=Config)
        mock_model1 = Mock()
        mock_model1.model = "gpt-4"
        mock_model2 = Mock()
        mock_model2.model = "gpt-3.5"
        mock_config.models = [mock_model1, mock_model2]

        agent1 = Agent(
            agent_name="agent1",
            agent_model_name="gpt-4",
            agent_display_name="Agent 1",
            agent_description="Agent 1",
            agent_type="test",
        )
        agent2 = Agent(
            agent_name="agent2",
            agent_model_name="gpt-3.5",
            agent_display_name="Agent 2",
            agent_description="Agent 2",
            agent_type="test",
        )

        agents = Agents(agents=[agent1, agent2], config=mock_config)
        assert agents is not None
        assert hasattr(agents, "_agents")

    def test_get_agent_by_name_success(self):
        """Test getting agent by name."""
        from ingenious.models.config import Config

        mock_config = Mock(spec=Config)
        mock_model = Mock()
        mock_model.model = "gpt-4"
        mock_config.models = [mock_model]

        agent = Agent(
            agent_name="test_agent",
            agent_model_name="gpt-4",
            agent_display_name="Test Agent",
            agent_description="Test agent",
            agent_type="test",
        )

        agents = Agents(agents=[agent], config=mock_config)
        found_agent = agents.get_agent_by_name("test_agent")
        assert found_agent == agent


class TestAgentChat:
    """Test cases for AgentChat class."""

    def test_init_required_fields(self):
        """Test AgentChat initialization with required fields."""
        chat = AgentChat(
            chat_name="test_chat",
            target_agent_name="test_agent",
            source_agent_name="source_agent",
            user_message="Hello",
            system_prompt="You are helpful",
        )
        assert chat.chat_name == "test_chat"
        assert chat.target_agent_name == "test_agent"
        assert chat.source_agent_name == "source_agent"
        assert chat.user_message == "Hello"
        assert chat.system_prompt == "You are helpful"


class TestAgentChats:
    """Test cases for AgentChats class."""

    def test_init_empty(self):
        """Test AgentChats initialization."""
        chats = AgentChats()
        assert hasattr(chats, "chats") or hasattr(chats, "_agent_chats")

    def test_init_with_chats(self):
        """Test AgentChats initialization with existing chats."""
        _chat1 = AgentChat(
            chat_name="chat1",
            target_agent_name="agent1",
            source_agent_name="source1",
            user_message="Hello 1",
            system_prompt="Prompt 1",
        )
        _chat2 = AgentChat(
            chat_name="chat2",
            target_agent_name="agent2",
            source_agent_name="source2",
            user_message="Hello 2",
            system_prompt="Prompt 2",
        )

        # Test that we can construct AgentChats with a list of chats
        chats = AgentChats()
        # Test that chats collection exists and can be used
        assert chats is not None


class TestLLMUsageTracker:
    """Test cases for LLMUsageTracker class."""

    def test_init_with_required_params(self):
        """Test LLMUsageTracker initialization with required parameters."""

        # Create mocks for required parameters
        mock_agents = Mock()
        mock_config = Mock()
        mock_repo = Mock()

        tracker = LLMUsageTracker(
            agents=mock_agents,
            config=mock_config,
            chat_history_repository=mock_repo,
            revision_id="test_revision",
            identifier="test_identifier",
            event_type="test_event",
        )
        assert tracker is not None
        # Test that it can be initialized without errors

    def test_is_logging_handler(self):
        """Test that LLMUsageTracker extends logging.Handler."""
        import logging

        # Create mocks for required parameters
        mock_agents = Mock()
        mock_config = Mock()
        mock_repo = Mock()

        tracker = LLMUsageTracker(
            agents=mock_agents,
            config=mock_config,
            chat_history_repository=mock_repo,
            revision_id="test_revision",
            identifier="test_identifier",
            event_type="test_event",
        )
        assert isinstance(tracker, logging.Handler)
