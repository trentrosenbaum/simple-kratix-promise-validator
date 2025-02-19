"""Tests covering the validate functions"""
import io
from unittest.mock import patch, mock_open
import pytest
from validate import load_yaml, validate_resource

# pylint: disable=W0613
def valid_mock_file_open(filename, *args, **kwargs):
    """Custom open() mock to handle multiple files and support encoding."""
    file_contents = {
        "promise.yaml": """
        spec:
          api:
            spec:
              versions:
                - schema:
                    openAPIV3Schema:
                      type: object
                      properties:
                        name:
                          type: string
                        age:
                          type: integer
        """,
        "resource.yaml": """
        name: John Doe
        age: 30
        """,
    }

    if filename in file_contents:
        return io.StringIO(file_contents[filename])
    raise FileNotFoundError(f"File {filename} not found")


def invalid_mock_file_open(filename, *args, **kwargs):
    """Custom open() mock to handle multiple files and support encoding."""
    file_contents = {
        "promise.yaml": """
        spec:
          api:
            spec:
              versions:
                - schema:
                    openAPIV3Schema:
                      type: object
                      properties:
                        name:
                          type: string
                        age:
                          type: integer
        """,
        "resource.yaml": """
        name: John Doe
        age: "thirty"  # Invalid type for age
        """,
    }

    if filename in file_contents:
        return io.StringIO(file_contents[filename])
    raise FileNotFoundError(f"File {filename} not found")

def test_valid_resource():
    """Tests an expected valid response"""
    with patch('builtins.open', side_effect=valid_mock_file_open), \
            patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:

        validate_resource("promise.yaml", "resource.yaml")

        assert "✅ Validation successful" in mock_stdout.getvalue()

def test_invalid_resource():
    """Tests an expected invalid response"""
    with patch('builtins.open', side_effect=invalid_mock_file_open), \
         patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:

        validate_resource("promise.yaml", "resource.yaml")

        assert "❌ Validation failed" in mock_stdout.getvalue()
        assert "'thirty' is not of type 'integer'" in mock_stdout.getvalue()





def test_missing_key():
    """Tests the schema validates a missing required key"""
    promise_yaml = """
    spec:
      api:
        spec:
          versions:
            - schema:
                openAPIV3Schema:
                  type: object
                  required: [age]  # Make age required
                  properties:
                    name:
                      type: string
                    age:
                      type: integer
    """
    resource_yaml = """
    name: John Doe  # Missing 'age'
    """

    with patch('builtins.open', mock_open(read_data=resource_yaml)), \
            patch('builtins.open', mock_open(read_data=promise_yaml)), \
            patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:

        validate_resource("promise.yaml", "resource.yaml")

        assert "❌ Validation failed" in mock_stdout.getvalue()
        assert "'age' is a required property" in mock_stdout.getvalue() # Correct error message

def test_invalid_promise_yaml():
    """Tests that an invalid promise fails validations"""

    promise_yaml = """
    invalid_yaml:  # Missing spec.api.spec.versions[0].schema.openAPIV3Schema
    """
    resource_yaml = """
    name: John Doe
    age: 30
    """

    with patch('builtins.open', mock_open(read_data=resource_yaml)), \
            patch('builtins.open', mock_open(read_data=promise_yaml)), \
            patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:

        validate_resource("promise.yaml", "resource.yaml")

        # Check for the *specific* error message printed before sys.exit
        assert "⚠️ Error: Missing key 'spec' in the Promise YAML.\n" in mock_stdout.getvalue()


def test_file_not_found():
    """Tests a file not found is reported"""
    with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
        with pytest.raises(SystemExit):
            load_yaml("nonexistent_file.yaml")
        assert "Error: File not found: nonexistent_file.yaml" in mock_stdout.getvalue()


def test_invalid_yaml():
    """Test incorrect YAML is reported"""
    yaml_content = """
    name John Doe  # Missing colon after 'name'
    age: 30
    """
    with patch('builtins.open', mock_open(read_data=yaml_content)), \
            patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:

        with pytest.raises(SystemExit):
            load_yaml("file.yaml")

        assert "YAML Parsing Error" in mock_stdout.getvalue()  # Check for the correct message
