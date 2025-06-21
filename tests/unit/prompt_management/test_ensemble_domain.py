"""
Tests for the ensemble domain models and entities.

This module tests the core domain logic for prompt ensembles,
including configuration validation and execution tracking.
"""

from datetime import datetime

import pytest

from ingenious.prompt_management.domain.ensemble import (
    AgentExecution,
    AgentRole,
    EnsembleConfiguration,
    EnsembleExecution,
    EnsemblePromptTemplate,
    EnsembleResult,
    EnsembleStrategy,
)


class TestEnsemblePromptTemplate:
    """Test ensemble prompt template functionality."""

    def test_create_template_with_defaults(self):
        """Test creating a template with default values."""
        template = EnsemblePromptTemplate(
            name="test_template",
            content="Analyze: {{ content }}",
            role=AgentRole.ANALYZER,
        )

        assert template.name == "test_template"
        assert template.content == "Analyze: {{ content }}"
        assert template.role == AgentRole.ANALYZER
        assert template.priority == 1
        assert template.dependencies == []
        assert template.variables == {}
        assert template.template_id is not None
        assert isinstance(template.created_at, datetime)

    def test_create_template_with_custom_values(self):
        """Test creating a template with custom values."""
        template = EnsemblePromptTemplate(
            name="critic_template",
            content="Critique: {{ content }}",
            role=AgentRole.CRITIC,
            priority=2,
            dependencies=["analyzer_template"],
            variables={"style": "harsh"},
        )

        assert template.name == "critic_template"
        assert template.role == AgentRole.CRITIC
        assert template.priority == 2
        assert template.dependencies == ["analyzer_template"]
        assert template.variables == {"style": "harsh"}


class TestEnsembleConfiguration:
    """Test ensemble configuration functionality."""

    def test_create_basic_configuration(self):
        """Test creating a basic ensemble configuration."""
        sub_templates = [
            EnsemblePromptTemplate(
                name="analyzer",
                content="Analyze: {{ content }}",
                role=AgentRole.ANALYZER,
            ),
            EnsemblePromptTemplate(
                name="critic",
                content="Critique: {{ content }}",
                role=AgentRole.CRITIC,
            ),
        ]

        config = EnsembleConfiguration(
            name="test_ensemble",
            description="Test configuration",
            main_prompt_template="Process: {{ content }}",
            sub_prompt_templates=sub_templates,
            reduce_prompt_template="Combine: {{ responses }}",
        )

        assert config.name == "test_ensemble"
        assert config.description == "Test configuration"
        assert config.strategy == EnsembleStrategy.PARALLEL
        assert len(config.sub_prompt_templates) == 2
        assert config.max_concurrent_agents == 5
        assert config.timeout_seconds == 300
        assert config.config_id is not None

    def test_configuration_with_custom_strategy(self):
        """Test configuration with custom strategy."""
        config = EnsembleConfiguration(
            name="sequential_ensemble",
            main_prompt_template="Process: {{ content }}",
            sub_prompt_templates=[],
            reduce_prompt_template="Combine: {{ responses }}",
            strategy=EnsembleStrategy.SEQUENTIAL,
            max_concurrent_agents=3,
            timeout_seconds=600,
        )

        assert config.strategy == EnsembleStrategy.SEQUENTIAL
        assert config.max_concurrent_agents == 3
        assert config.timeout_seconds == 600


class TestAgentExecution:
    """Test agent execution tracking."""

    def test_create_agent_execution(self):
        """Test creating an agent execution record."""
        execution = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_123",
            prompt="Analyze this content",
        )

        assert execution.agent_role == AgentRole.ANALYZER
        assert execution.template_id == "template_123"
        assert execution.prompt == "Analyze this content"
        assert execution.response is None
        assert execution.error is None
        assert execution.execution_id is not None

    def test_successful_execution(self):
        """Test tracking a successful execution."""
        execution = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_123",
            prompt="Analyze this content",
            response="Analysis complete",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            completed_at=datetime(2024, 1, 1, 10, 0, 30),
        )

        assert execution.is_successful is True
        assert execution.duration_seconds == 30.0

    def test_failed_execution(self):
        """Test tracking a failed execution."""
        execution = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_123",
            prompt="Analyze this content",
            error="API timeout",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            completed_at=datetime(2024, 1, 1, 10, 1, 0),
        )

        assert execution.is_successful is False
        assert execution.duration_seconds == 60.0

    def test_duration_calculation(self):
        """Test duration calculation."""
        execution = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_123",
            prompt="Test prompt",
        )

        # No timestamps set
        assert execution.duration_seconds is None

        # Only start time set
        execution.started_at = datetime(2024, 1, 1, 10, 0, 0)
        assert execution.duration_seconds is None

        # Both timestamps set
        execution.completed_at = datetime(2024, 1, 1, 10, 0, 15)
        assert execution.duration_seconds == 15.0


class TestEnsembleExecution:
    """Test ensemble execution tracking."""

    def test_create_ensemble_execution(self):
        """Test creating an ensemble execution record."""
        execution = EnsembleExecution(
            config_id="config_123",
            input_data={"content": "test content"},
        )

        assert execution.config_id == "config_123"
        assert execution.input_data == {"content": "test content"}
        assert execution.status == "running"
        assert execution.agent_executions == []
        assert execution.total_tokens_used == 0
        assert execution.execution_id is not None

    def test_add_agent_execution(self):
        """Test adding agent executions to ensemble."""
        ensemble_exec = EnsembleExecution(
            config_id="config_123",
            input_data={"content": "test"},
        )

        agent_exec = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_123",
            prompt="Test prompt",
            response="Test response",
            token_usage={"total_tokens": 100},
        )

        ensemble_exec.add_agent_execution(agent_exec)

        assert len(ensemble_exec.agent_executions) == 1
        assert ensemble_exec.total_tokens_used == 100

    def test_successful_and_failed_executions(self):
        """Test filtering successful and failed executions."""
        ensemble_exec = EnsembleExecution(
            config_id="config_123",
            input_data={"content": "test"},
        )

        # Add successful execution
        successful_exec = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_1",
            prompt="Test prompt",
            response="Test response",
        )
        ensemble_exec.add_agent_execution(successful_exec)

        # Add failed execution
        failed_exec = AgentExecution(
            agent_role=AgentRole.CRITIC,
            template_id="template_2",
            prompt="Test prompt",
            error="API error",
        )
        ensemble_exec.add_agent_execution(failed_exec)

        assert len(ensemble_exec.successful_executions) == 1
        assert len(ensemble_exec.failed_executions) == 1
        assert ensemble_exec.successful_executions[0].agent_role == AgentRole.ANALYZER
        assert ensemble_exec.failed_executions[0].agent_role == AgentRole.CRITIC


class TestEnsembleResult:
    """Test ensemble result creation and management."""

    def test_create_result_from_execution(self):
        """Test creating a result from execution and configuration."""
        # Create configuration
        config = EnsembleConfiguration(
            name="test_ensemble",
            main_prompt_template="Process: {{ content }}",
            sub_prompt_templates=[],
            reduce_prompt_template="Combine: {{ responses }}",
        )

        # Create execution with agent results
        execution = EnsembleExecution(
            config_id=config.config_id,
            input_data={"content": "test"},
            final_response="Final analysis result",
            completed_at=datetime(2024, 1, 1, 10, 1, 0),
            total_tokens_used=250,
        )
        execution.started_at = datetime(2024, 1, 1, 10, 0, 0)

        # Add agent executions
        agent_exec1 = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_1",
            prompt="Test prompt",
            response="Analysis response",
        )
        agent_exec2 = AgentExecution(
            agent_role=AgentRole.CRITIC,
            template_id="template_2",
            prompt="Test prompt",
            response="Critic response",
        )
        execution.add_agent_execution(agent_exec1)
        execution.add_agent_execution(agent_exec2)

        # Create result
        result = EnsembleResult.from_execution(execution, config)

        assert result.execution_id == execution.execution_id
        assert result.config_name == config.name
        assert result.final_response == "Final analysis result"
        assert len(result.agent_responses) == 2
        assert result.agent_responses[AgentRole.ANALYZER] == "Analysis response"
        assert result.agent_responses[AgentRole.CRITIC] == "Critic response"

        # Check execution stats
        stats = result.execution_stats
        assert stats["total_duration_seconds"] == 60.0
        assert stats["total_tokens_used"] == 250
        assert stats["successful_agents"] == 2
        assert stats["failed_agents"] == 0

    def test_result_with_failed_executions(self):
        """Test result creation with some failed executions."""
        config = EnsembleConfiguration(
            name="test_ensemble",
            main_prompt_template="Process: {{ content }}",
            sub_prompt_templates=[],
            reduce_prompt_template="Combine: {{ responses }}",
        )

        execution = EnsembleExecution(
            config_id=config.config_id,
            input_data={"content": "test"},
            final_response="Partial result",
        )

        # Add successful execution
        successful_exec = AgentExecution(
            agent_role=AgentRole.ANALYZER,
            template_id="template_1",
            prompt="Test prompt",
            response="Success response",
        )
        execution.add_agent_execution(successful_exec)

        # Add failed execution
        failed_exec = AgentExecution(
            agent_role=AgentRole.CRITIC,
            template_id="template_2",
            prompt="Test prompt",
            error="API timeout",
        )
        execution.add_agent_execution(failed_exec)

        result = EnsembleResult.from_execution(execution, config)

        # Only successful responses should be included
        assert len(result.agent_responses) == 1
        assert result.agent_responses[AgentRole.ANALYZER] == "Success response"
        assert AgentRole.CRITIC not in result.agent_responses

        # Stats should reflect both successful and failed
        stats = result.execution_stats
        assert stats["successful_agents"] == 1
        assert stats["failed_agents"] == 1


@pytest.fixture
def sample_ensemble_config():
    """Fixture providing a sample ensemble configuration."""
    sub_templates = [
        EnsemblePromptTemplate(
            name="analyzer",
            content="Analyze the following content: {{ content }}",
            role=AgentRole.ANALYZER,
            priority=1,
        ),
        EnsemblePromptTemplate(
            name="critic",
            content="Critically evaluate: {{ content }}",
            role=AgentRole.CRITIC,
            priority=2,
        ),
        EnsemblePromptTemplate(
            name="synthesizer",
            content="Synthesize the analysis and critique of: {{ content }}",
            role=AgentRole.SYNTHESIZER,
            priority=3,
            dependencies=["analyzer", "critic"],
        ),
    ]

    return EnsembleConfiguration(
        name="comprehensive_analysis",
        description="Multi-perspective analysis ensemble",
        strategy=EnsembleStrategy.HIERARCHICAL,
        main_prompt_template="Perform comprehensive analysis of: {{ content }}",
        sub_prompt_templates=sub_templates,
        reduce_prompt_template="""
        Create final report from:
        {% for role, response in agent_responses.items() %}
        {{ role }}: {{ response }}
        {% endfor %}
        """,
        max_concurrent_agents=3,
        timeout_seconds=600,
        variables={"analysis_depth": "comprehensive"},
    )


class TestEnsembleConfigurationIntegration:
    """Integration tests for ensemble configuration."""

    def test_hierarchical_configuration(self, sample_ensemble_config):
        """Test hierarchical configuration with dependencies."""
        config = sample_ensemble_config

        assert config.strategy == EnsembleStrategy.HIERARCHICAL
        assert len(config.sub_prompt_templates) == 3

        # Check dependency structure
        synthesizer_template = next(
            t for t in config.sub_prompt_templates if t.role == AgentRole.SYNTHESIZER
        )
        assert len(synthesizer_template.dependencies) == 2
        assert "analyzer" in synthesizer_template.dependencies
        assert "critic" in synthesizer_template.dependencies

    def test_configuration_serialization(self, sample_ensemble_config):
        """Test that configuration can be serialized and deserialized."""
        config = sample_ensemble_config

        # Convert to dict (simulating JSON serialization)
        config_dict = config.model_dump()

        # Recreate from dict
        restored_config = EnsembleConfiguration(**config_dict)

        assert restored_config.name == config.name
        assert restored_config.strategy == config.strategy
        assert len(restored_config.sub_prompt_templates) == len(
            config.sub_prompt_templates
        )
        assert restored_config.variables == config.variables
