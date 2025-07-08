"""
Unit tests for utility functions.
"""

from ingenious.utils.conversation_builder import (
    build_assistant_message,
    build_system_prompt,
    build_user_message,
)
from ingenious.utils.lazy_group import LazyGroup
from ingenious.utils.log_levels import LogLevel
from ingenious.utils.model_utils import (
    Dict_To_Csv,
    Get_Model_Properties,
    Is_Non_Complex_Field_Check_By_Type,
    Is_Non_Complex_Field_Check_By_Value,
    List_To_Csv,
    Listable_Object_To_Csv,
    Object_To_Markdown,
    Object_To_Yaml,
)

# load_sample_data import removed - function doesn't exist


class TestConversationBuilder:
    """Test cases for conversation builder functions."""

    def test_build_system_prompt(self):
        """Test building system prompt message."""
        content = "You are a helpful assistant."
        message = build_system_prompt(content)

        assert message["role"] == "system"
        assert message["content"] == content

    def test_build_user_message(self):
        """Test building user message."""
        content = "Hello, how are you?"
        message = build_user_message(content, user_name=None)

        assert message["role"] == "user"
        assert message["content"] == content

    def test_build_assistant_message(self):
        """Test building assistant message."""
        content = "I'm doing well, thank you!"
        message = build_assistant_message(content)

        assert message["role"] == "assistant"
        assert message["content"] == content

    def test_build_user_message_with_name(self):
        """Test building user message with user name."""
        content = "Hello, how are you?"
        user_name = "john"
        message = build_user_message(content, user_name)

        assert message["role"] == "user"
        assert message["content"] == content
        assert message["name"] == user_name

    def test_build_assistant_message_with_tool_calls(self):
        """Test building assistant message with tool calls."""
        content = "I'll help you with that."
        tool_calls = [{"id": "1", "function": {"name": "test_function"}}]
        message = build_assistant_message(content, tool_calls)

        assert message["role"] == "assistant"
        assert message["content"] == content
        assert message["tool_calls"] == tool_calls


class TestModelUtils:
    """Test cases for model utility functions."""

    def test_is_non_complex_field_check_by_value_simple_types(self):
        """Test non-complex field check with simple types."""
        assert Is_Non_Complex_Field_Check_By_Value("string") is True
        assert Is_Non_Complex_Field_Check_By_Value(123) is True
        assert Is_Non_Complex_Field_Check_By_Value(45.67) is True
        assert Is_Non_Complex_Field_Check_By_Value(True) is True
        assert Is_Non_Complex_Field_Check_By_Value(None) is True

    def test_is_non_complex_field_check_by_value_complex_types(self):
        """Test non-complex field check with complex types."""
        assert Is_Non_Complex_Field_Check_By_Value([1, 2, 3]) is False
        assert Is_Non_Complex_Field_Check_By_Value({"key": "value"}) is False
        assert Is_Non_Complex_Field_Check_By_Value(object()) is False

    def test_is_non_complex_field_check_by_type_simple_types(self):
        """Test non-complex field check by type with simple types."""
        assert Is_Non_Complex_Field_Check_By_Type(str) is True
        assert Is_Non_Complex_Field_Check_By_Type(int) is True
        assert Is_Non_Complex_Field_Check_By_Type(float) is True
        assert Is_Non_Complex_Field_Check_By_Type(bool) is True
        assert Is_Non_Complex_Field_Check_By_Type(type(None)) is True

    def test_is_non_complex_field_check_by_type_complex_types(self):
        """Test non-complex field check by type with complex types."""
        assert Is_Non_Complex_Field_Check_By_Type("RootModel[list]") is False
        assert Is_Non_Complex_Field_Check_By_Type("RootModel[dict]") is False
        assert Is_Non_Complex_Field_Check_By_Type("RootModel[object]") is False

    def test_get_model_properties_simple_object(self):
        """Test getting model properties from simple object."""
        from pydantic import BaseModel

        class SimpleModel(BaseModel):
            name: str = "test"
            age: int = 25
            active: bool = True

        obj = SimpleModel()
        properties = Get_Model_Properties(obj)

        assert len(properties) == 3
        field_names = [prop.FieldName for prop in properties]
        assert "name" in field_names
        assert "age" in field_names
        assert "active" in field_names

    def test_dict_to_csv_simple_dict(self):
        """Test converting simple dictionary to CSV."""
        data = {"row1": {"name": "John", "age": 30, "city": "New York"}}
        row_header_columns = ["name", "age", "city"]
        csv_content = Dict_To_Csv(data, row_header_columns, "test")

        assert "``` csv" in csv_content
        assert "name,age,city" in csv_content
        assert "John,30,New York" in csv_content

    def test_list_to_csv_simple_list(self):
        """Test converting simple list to CSV."""
        data = [{"name": "apple"}, {"name": "banana"}, {"name": "cherry"}]
        row_header_columns = ["name"]
        csv_content = List_To_Csv(data, row_header_columns, "test")

        assert "``` csv" in csv_content
        assert "name" in csv_content
        assert "apple" in csv_content

    def test_listable_object_to_csv_dict(self):
        """Test converting listable object (dict) to CSV."""
        from pydantic import BaseModel

        class Person(BaseModel):
            name: str
            age: int

        data = [Person(name="John", age=30), Person(name="Jane", age=25)]
        row_type = Person(name="dummy", age=0)
        csv_content = Listable_Object_To_Csv(data, row_type)

        assert "``` csv" in csv_content
        assert "name" in csv_content
        assert "John" in csv_content

    def test_listable_object_to_csv_list(self):
        """Test converting listable object (list) to CSV."""
        from pydantic import BaseModel

        class Item(BaseModel):
            value: str

        data = [Item(value="item1"), Item(value="item2")]
        row_type = Item(value="dummy")
        csv_content = Listable_Object_To_Csv(data, row_type)

        assert "``` csv" in csv_content
        assert "value" in csv_content

    def test_object_to_yaml_simple_object(self):
        """Test converting object to YAML."""

        class SimpleModel:
            def __init__(self):
                self.name = "test"
                self.age = 25

        obj = SimpleModel()
        yaml_content = Object_To_Yaml(obj)

        assert "name: test" in yaml_content
        assert "age: 25" in yaml_content

    def test_object_to_markdown_simple_object(self):
        """Test converting object to Markdown."""

        class SimpleModel:
            def __init__(self):
                self.name = "test"
                self.age = 25

        obj = SimpleModel()
        markdown_content = Object_To_Markdown(obj, "test_object")

        assert isinstance(markdown_content, str)
        assert len(markdown_content) > 0


class TestLazyGroup:
    """Test cases for LazyGroup class."""

    def test_init(self):
        """Test LazyGroup initialization."""
        group = LazyGroup()
        assert hasattr(group, "_loaders")
        assert isinstance(group._loaders, dict)


class TestLogLevel:
    """Test cases for LogLevel class."""

    def test_log_level_class_exists(self):
        """Test that LogLevel class can be imported."""
        assert LogLevel is not None

    def test_log_level_constants(self):
        """Test that LogLevel constants are defined."""
        assert LogLevel.DEBUG == 0
        assert LogLevel.INFO == 1
        assert LogLevel.WARNING == 2
        assert LogLevel.ERROR == 3

    def test_from_string_valid(self):
        """Test converting valid string to log level."""
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_string("INFO") == LogLevel.INFO
        assert LogLevel.from_string("WARNING") == LogLevel.WARNING
        assert LogLevel.from_string("ERROR") == LogLevel.ERROR

    def test_from_string_invalid(self):
        """Test converting invalid string to log level."""
        assert LogLevel.from_string("INVALID") is None

    def test_to_string_valid(self):
        """Test converting valid log level to string."""
        assert LogLevel.to_string(LogLevel.DEBUG) == "DEBUG"
        assert LogLevel.to_string(LogLevel.INFO) == "INFO"
        assert LogLevel.to_string(LogLevel.WARNING) == "WARNING"
        assert LogLevel.to_string(LogLevel.ERROR) == "ERROR"

    def test_to_string_invalid(self):
        """Test converting invalid log level to string."""
        assert LogLevel.to_string(999) == "Unknown"


# TestLoadSampleData removed - function doesn't exist
