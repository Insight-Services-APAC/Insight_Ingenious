"""
Tests for the ensemble orchestration service.

This module tests the core orchestration logic for executing
prompt ensembles in various strategies and configurations.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.prompt_management.application.ensemble_service import (
    EnsembleOrchestrationService,
)
from ingenious.prompt_management.domain.ensemble import (
    AgentExecution,
    AgentRole,
    EnsembleConfiguration,
    EnsemblePromptTemplate,
    EnsembleStrategy,
)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    service = AsyncMock()
    service.generate_response = AsyncMock()
    return service


@pytest.fixture
def orchestration_service(mock_llm_service):
    """Create orchestration service with mocked dependencies."""
    return EnsembleOrchestrationService(mock_llm_service)


@pytest.fixture
def sample_parallel_config():
    """Sample configuration for parallel execution."""
    sub_templates = [
        EnsemblePromptTemplate(
            name="analyzer",
            content="Analyze: {{ content }}",
            role=AgentRole.ANALYZER,
            priority=1,
        ),
        EnsemblePromptTemplate(
            name="critic",
            content="Critique: {{ content }}",
            role=AgentRole.CRITIC,
            priority=1,
        ),
    ]

    return EnsembleConfiguration(
        name="parallel_test",
        strategy=EnsembleStrategy.PARALLEL,
        main_prompt_template="Process: {{ content }}",
        sub_prompt_templates=sub_templates,
        reduce_prompt_template="Combine: {% for role, response in agent_responses.items() %}{{ response }}{% endfor %}",
        max_concurrent_agents=2,
    )


@pytest.fixture
def sample_sequential_config():
    """Sample configuration for sequential execution."""
    sub_templates = [
        EnsemblePromptTemplate(
            name="first_analysis",
            content="Initial analysis: {{ content }}",
            role=AgentRole.ANALYZER,
            priority=1,
        ),
        EnsemblePromptTemplate(
            name="second_review",
            content="Review analysis: {{ content }}",
            role=AgentRole.REVIEWER,
            priority=2,
        ),
    ]

    return EnsembleConfiguration(
        name="sequential_test",
        strategy=EnsembleStrategy.SEQUENTIAL,
        main_prompt_template="Process: {{ content }}",
        sub_prompt_templates=sub_templates,
        reduce_prompt_template="Final: {% for role, response in agent_responses.items() %}{{ response }}{% endfor %}",
    )


@pytest.fixture
def sample_hierarchical_config():
    """Sample configuration for hierarchical execution."""
    sub_templates = [
        EnsemblePromptTemplate(
            template_id="template_1",
            name="base_analysis",
            content="Base analysis: {{ content }}",
            role=AgentRole.ANALYZER,
            priority=1,
            dependencies=[],
        ),
        EnsemblePromptTemplate(
            template_id="template_2",
            name="dependent_review",
            content="Review based on analysis: {{ content }}",
            role=AgentRole.REVIEWER,
            priority=2,
            dependencies=["template_1"],
        ),
    ]

    return EnsembleConfiguration(
        name="hierarchical_test",
        strategy=EnsembleStrategy.HIERARCHICAL,
        main_prompt_template="Process: {{ content }}",
        sub_prompt_templates=sub_templates,
        reduce_prompt_template="Final: {% for role, response in agent_responses.items() %}{{ response }}{% endfor %}",
    )


class TestEnsembleOrchestrationService:
    """Test the ensemble orchestration service."""

    @pytest.mark.asyncio
    async def test_generate_sub_prompts(
        self, orchestration_service, sample_parallel_config
    ):
        """Test sub-prompt generation from templates."""
        input_data = {"content": "test content"}

        sub_prompts = await orchestration_service._generate_sub_prompts(
            sample_parallel_config, input_data
        )

        assert len(sub_prompts) == 2

        # Check first prompt
        analyzer_prompt = next(
            p for p in sub_prompts if p["role"] == AgentRole.ANALYZER
        )
        assert analyzer_prompt["prompt"] == "Analyze: test content"
        assert analyzer_prompt["priority"] == 1

        # Check second prompt
        critic_prompt = next(p for p in sub_prompts if p["role"] == AgentRole.CRITIC)
        assert critic_prompt["prompt"] == "Critique: test content"
        assert critic_prompt["priority"] == 1

    @pytest.mark.asyncio
    async def test_generate_sub_prompts_with_variables(self, orchestration_service):
        """Test sub-prompt generation with template variables."""
        template = EnsemblePromptTemplate(
            name="test_template",
            content="Analyze {{ content }} with {{ style }} approach",
            role=AgentRole.ANALYZER,
            variables={"style": "detailed"},
        )

        config = EnsembleConfiguration(
            name="test",
            main_prompt_template="Process: {{ content }}",
            sub_prompt_templates=[template],
            reduce_prompt_template="Result: {{ response }}",
            variables={"default_var": "value"},
        )

        input_data = {"content": "test content"}

        sub_prompts = await orchestration_service._generate_sub_prompts(
            config, input_data
        )

        assert len(sub_prompts) == 1
        assert sub_prompts[0]["prompt"] == "Analyze test content with detailed approach"

    @pytest.mark.asyncio
    async def test_execute_single_agent(self, orchestration_service, mock_llm_service):
        """Test single agent execution."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = "Agent response"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_llm_service.generate_response.return_value = mock_response

        sub_prompt = {
            "role": AgentRole.ANALYZER,
            "template_id": "template_123",
            "prompt": "Test prompt",
        }

        execution = await orchestration_service._execute_single_agent(sub_prompt)

        assert execution.agent_role == AgentRole.ANALYZER
        assert execution.template_id == "template_123"
        assert execution.prompt == "Test prompt"
        assert execution.response == "Agent response"
        assert execution.error is None
        assert execution.is_successful is True
        assert execution.token_usage["total_tokens"] == 30

        # Verify LLM was called correctly
        mock_llm_service.generate_response.assert_called_once()
        call_args = mock_llm_service.generate_response.call_args[0][0]
        assert call_args[0]["role"] == "user"
        assert call_args[0]["content"] == "Test prompt"

    @pytest.mark.asyncio
    async def test_execute_single_agent_with_error(
        self, orchestration_service, mock_llm_service
    ):
        """Test single agent execution with error."""
        # Setup mock to raise exception
        mock_llm_service.generate_response.side_effect = Exception("API Error")

        sub_prompt = {
            "role": AgentRole.ANALYZER,
            "template_id": "template_123",
            "prompt": "Test prompt",
        }

        execution = await orchestration_service._execute_single_agent(sub_prompt)

        assert execution.agent_role == AgentRole.ANALYZER
        assert execution.template_id == "template_123"
        assert execution.response is None
        assert execution.error == "API Error"
        assert execution.is_successful is False

    @pytest.mark.asyncio
    async def test_execute_parallel(self, orchestration_service, mock_llm_service):
        """Test parallel execution of sub-prompts."""
        # Setup mock responses
        mock_response1 = Mock()
        mock_response1.content = "Response 1"
        mock_response2 = Mock()
        mock_response2.content = "Response 2"

        mock_llm_service.generate_response.side_effect = [
            mock_response1,
            mock_response2,
        ]

        sub_prompts = [
            {
                "role": AgentRole.ANALYZER,
                "template_id": "template_1",
                "prompt": "Prompt 1",
                "priority": 1,
                "dependencies": [],
            },
            {
                "role": AgentRole.CRITIC,
                "template_id": "template_2",
                "prompt": "Prompt 2",
                "priority": 1,
                "dependencies": [],
            },
        ]

        executions = await orchestration_service._execute_parallel(
            sub_prompts, max_concurrent=2
        )

        assert len(executions) == 2
        assert all(exec.is_successful for exec in executions)
        assert executions[0].response == "Response 1"
        assert executions[1].response == "Response 2"

        # Both LLM calls should have been made
        assert mock_llm_service.generate_response.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_sequential(self, orchestration_service, mock_llm_service):
        """Test sequential execution of sub-prompts."""
        # Setup mock responses
        mock_response1 = Mock()
        mock_response1.content = "Sequential Response 1"
        mock_response2 = Mock()
        mock_response2.content = "Sequential Response 2"

        mock_llm_service.generate_response.side_effect = [
            mock_response1,
            mock_response2,
        ]

        sub_prompts = [
            {
                "role": AgentRole.ANALYZER,
                "template_id": "template_1",
                "prompt": "First prompt",
                "priority": 1,
                "dependencies": [],
            },
            {
                "role": AgentRole.REVIEWER,
                "template_id": "template_2",
                "prompt": "Second prompt",
                "priority": 2,
                "dependencies": [],
            },
        ]

        executions = await orchestration_service._execute_sequential(sub_prompts)

        assert len(executions) == 2
        assert all(exec.is_successful for exec in executions)
        assert executions[0].response == "Sequential Response 1"
        assert executions[1].response == "Sequential Response 2"

        # Verify sequential execution order
        assert mock_llm_service.generate_response.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_hierarchical(
        self, orchestration_service, mock_llm_service, sample_hierarchical_config
    ):
        """Test hierarchical execution with dependencies."""
        # Setup mock responses
        mock_response1 = Mock()
        mock_response1.content = "Base analysis result"
        mock_response2 = Mock()
        mock_response2.content = "Dependent review result"

        mock_llm_service.generate_response.side_effect = [
            mock_response1,
            mock_response2,
        ]

        sub_prompts = [
            {
                "template_id": "template_1",
                "role": AgentRole.ANALYZER,
                "prompt": "Base analysis prompt",
                "priority": 1,
                "dependencies": [],
            },
            {
                "template_id": "template_2",
                "role": AgentRole.REVIEWER,
                "prompt": "Dependent review prompt",
                "priority": 2,
                "dependencies": ["template_1"],
            },
        ]

        executions = await orchestration_service._execute_hierarchical(
            sub_prompts, sample_hierarchical_config
        )

        assert len(executions) == 2
        assert all(exec.is_successful for exec in executions)

        # Base analysis should execute first
        base_exec = next(
            exec for exec in executions if exec.template_id == "template_1"
        )
        assert base_exec.response == "Base analysis result"

        # Dependent review should execute after
        review_exec = next(
            exec for exec in executions if exec.template_id == "template_2"
        )
        assert review_exec.response == "Dependent review result"

    @pytest.mark.asyncio
    async def test_aggregate_results(self, orchestration_service, mock_llm_service):
        """Test result aggregation using reduce template."""
        # Setup mock response for aggregation
        mock_response = Mock()
        mock_response.content = "Aggregated final result"
        mock_llm_service.generate_response.return_value = mock_response

        # Create sample agent executions
        executions = [
            AgentExecution(
                agent_role=AgentRole.ANALYZER,
                template_id="template_1",
                prompt="Analyze prompt",
                response="Analysis result",
            ),
            AgentExecution(
                agent_role=AgentRole.CRITIC,
                template_id="template_2",
                prompt="Critique prompt",
                response="Critique result",
            ),
        ]

        reduce_template = "Combine: {% for role, response in agent_responses.items() %}{{ role }}: {{ response }}; {% endfor %}"
        input_data = {"content": "test content"}

        result = await orchestration_service._aggregate_results(
            reduce_template, executions, input_data
        )

        assert result == "Aggregated final result"

        # Verify reduce prompt was generated and sent to LLM
        mock_llm_service.generate_response.assert_called_once()
        call_args = mock_llm_service.generate_response.call_args[0][0]
        reduce_prompt = call_args[0]["content"]

        # Should contain agent responses
        assert "analyzer" in reduce_prompt
        assert "critic" in reduce_prompt
        assert "Analysis result" in reduce_prompt
        assert "Critique result" in reduce_prompt

    @pytest.mark.asyncio
    async def test_full_ensemble_execution_parallel(
        self, orchestration_service, mock_llm_service, sample_parallel_config
    ):
        """Test complete ensemble execution with parallel strategy."""
        # Setup mock responses
        mock_analysis = Mock()
        mock_analysis.content = "Analysis complete"
        mock_analysis.usage = Mock()
        mock_analysis.usage.prompt_tokens = 10
        mock_analysis.usage.completion_tokens = 15
        mock_analysis.usage.total_tokens = 25

        mock_critique = Mock()
        mock_critique.content = "Critique complete"
        mock_critique.usage = Mock()
        mock_critique.usage.prompt_tokens = 12
        mock_critique.usage.completion_tokens = 18
        mock_critique.usage.total_tokens = 30

        mock_aggregation = Mock()
        mock_aggregation.content = "Final aggregated result"
        mock_aggregation.usage = Mock()
        mock_aggregation.usage.prompt_tokens = 20
        mock_aggregation.usage.completion_tokens = 25
        mock_aggregation.usage.total_tokens = 45

        mock_llm_service.generate_response.side_effect = [
            mock_analysis,
            mock_critique,
            mock_aggregation,
        ]

        input_data = {"content": "test content for analysis"}

        result = await orchestration_service.execute_ensemble(
            sample_parallel_config, input_data
        )

        assert result.config_name == "parallel_test"
        assert result.final_response == "Final aggregated result"
        assert len(result.agent_responses) == 2
        assert result.agent_responses[AgentRole.ANALYZER] == "Analysis complete"
        assert result.agent_responses[AgentRole.CRITIC] == "Critique complete"

        # Should have made 3 LLM calls: 2 agents + 1 aggregation
        assert mock_llm_service.generate_response.call_count == 3

    @pytest.mark.asyncio
    async def test_ensemble_execution_with_partial_failure(
        self, orchestration_service, mock_llm_service, sample_parallel_config
    ):
        """Test ensemble execution when some agents fail."""
        # Setup mock responses - one success, one failure
        mock_success = Mock()
        mock_success.content = "Successful analysis"
        mock_success.usage = Mock()
        mock_success.usage.prompt_tokens = 10
        mock_success.usage.completion_tokens = 15
        mock_success.usage.total_tokens = 25

        mock_aggregation = Mock()
        mock_aggregation.content = "Partial result aggregation"
        mock_aggregation.usage = Mock()
        mock_aggregation.usage.prompt_tokens = 15
        mock_aggregation.usage.completion_tokens = 20
        mock_aggregation.usage.total_tokens = 35

        mock_llm_service.generate_response.side_effect = [
            mock_success,  # First agent succeeds
            Exception("API timeout"),  # Second agent fails
            mock_aggregation,  # Aggregation with partial results
        ]

        input_data = {"content": "test content"}

        result = await orchestration_service.execute_ensemble(
            sample_parallel_config, input_data
        )

        # Should still complete with partial results
        assert result.final_response == "Partial result aggregation"
        assert len(result.agent_responses) == 1  # Only successful response

        stats = result.execution_stats
        assert stats["successful_agents"] == 1
        assert stats["failed_agents"] == 1

    @pytest.mark.asyncio
    async def test_ensemble_execution_sequential(
        self, orchestration_service, mock_llm_service, sample_sequential_config
    ):
        """Test complete ensemble execution with sequential strategy."""
        # Setup mock responses
        mock_first = Mock()
        mock_first.content = "First analysis"
        mock_first.usage = Mock()
        mock_first.usage.prompt_tokens = 10
        mock_first.usage.completion_tokens = 15
        mock_first.usage.total_tokens = 25

        mock_second = Mock()
        mock_second.content = "Second review"
        mock_second.usage = Mock()
        mock_second.usage.prompt_tokens = 12
        mock_second.usage.completion_tokens = 18
        mock_second.usage.total_tokens = 30

        mock_final = Mock()
        mock_final.content = "Sequential final result"
        mock_final.usage = Mock()
        mock_final.usage.prompt_tokens = 20
        mock_final.usage.completion_tokens = 25
        mock_final.usage.total_tokens = 45

        mock_llm_service.generate_response.side_effect = [
            mock_first,
            mock_second,
            mock_final,
        ]

        input_data = {"content": "sequential test content"}

        result = await orchestration_service.execute_ensemble(
            sample_sequential_config, input_data
        )

        assert result.config_name == "sequential_test"
        assert result.final_response == "Sequential final result"
        assert len(result.agent_responses) == 2

        # Verify all calls were made in sequence
        assert mock_llm_service.generate_response.call_count == 3

    @pytest.mark.asyncio
    async def test_ensemble_execution_error_handling(
        self, orchestration_service, mock_llm_service, sample_parallel_config
    ):
        """Test error handling during ensemble execution."""
        # Mock LLM service to always fail
        mock_llm_service.generate_response.side_effect = Exception(
            "Critical API failure"
        )

        input_data = {"content": "test content"}

        # When all agents fail, the ensemble should complete but with empty fallback response
        result = await orchestration_service.execute_ensemble(
            sample_parallel_config, input_data
        )

        # Should complete with fallback aggregation (empty string since no successful agents)
        assert result.final_response == ""
        assert len(result.agent_responses) == 0  # No successful responses

        stats = result.execution_stats
        assert stats["successful_agents"] == 0
        assert stats["failed_agents"] == 2

    @pytest.mark.asyncio
    async def test_invalid_strategy_error(self, orchestration_service):
        """Test error handling for invalid execution strategy."""
        # Create a valid config first, then manually modify strategy to test error handling
        config = EnsembleConfiguration(
            name="invalid_test",
            strategy=EnsembleStrategy.PARALLEL,  # Start with valid strategy
            main_prompt_template="Process: {{ content }}",
            sub_prompt_templates=[],
            reduce_prompt_template="Result: {{ response }}",
        )

        # Manually set invalid strategy to test error handling in the service
        config.strategy = "invalid_strategy"

        input_data = {"content": "test content"}

        with pytest.raises(ValueError) as exc_info:
            await orchestration_service.execute_ensemble(config, input_data)

        assert "Unsupported strategy" in str(exc_info.value)
