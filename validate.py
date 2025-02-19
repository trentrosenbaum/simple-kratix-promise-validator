"""
This module validates a resource YAML file against a schema defined in a Promise YAML file.
"""
import json
import sys
import yaml
from jsonschema import validate, ValidationError

def load_yaml(file_path):
    """Load a YAML file and return its contents as a dictionary."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"YAML Parsing Error: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"OS Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        sys.exit(1)
    except Exception as e:  # Only catch general exception in validate to display remaining errors.
        print(f"Unexpected Error in load_yaml: {e}")
        sys.exit(1)

def validate_resource(promise_file, resource_file):
    """Validate the resource YAML against the schema in the Promise YAML."""
    try:
        # Load Promise and extract OpenAPI schema
        promise_data = load_yaml(promise_file)
        schema = promise_data["spec"]["api"]["spec"]["versions"][0]["schema"]["openAPIV3Schema"]

        # Ensure schema defines the top-level object type
        if "type" not in schema:
            schema["type"] = "object"

        # Load Resource YAML
        resource_data = load_yaml(resource_file)

        # Debug: Print extracted schema and resource
        print("Extracted Schema:\n", json.dumps(schema, indent=2))
        print("Resource Data:\n", json.dumps(resource_data, indent=2))

        # Validate the entire resource object, not just spec
        validate(instance=resource_data, schema=schema)

        print("✅ Validation successful: The resource is valid according to the Promise schema.")
    except ValidationError as e:
        print(f"❌ Validation failed: {e.message}")
    except KeyError as e:
        print(f"⚠️ Error: Missing key {e} in the Promise YAML.")
    except yaml.YAMLError as e:
        print(f"⚠️ YAML Parsing Error: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate.py <promise.yaml> <example-resource.yaml>")
        sys.exit(1)

    validate_resource(sys.argv[1], sys.argv[2])
