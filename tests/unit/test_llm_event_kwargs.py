from ingenious.domain.model.llm_event_kwargs import LLMEventKwargs


def test_llm_event_kwargs():
    """Test that we can import and use LLMEventKwargs."""
    kwargs = LLMEventKwargs(
        model="gpt-3.5-turbo",
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        cost=0.01,
        metadata={"test": "value"},
    )

    assert kwargs.model == "gpt-3.5-turbo"
    assert kwargs.prompt_tokens == 10
    assert kwargs.completion_tokens == 20
    assert kwargs.total_tokens == 30
    assert kwargs.cost == 0.01
    assert kwargs.metadata == {"test": "value"}

    # Test to_dict method
    kwargs_dict = kwargs.to_dict()
    assert kwargs_dict["model"] == "gpt-3.5-turbo"
    assert kwargs_dict["metadata"] == {"test": "value"}
