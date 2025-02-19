# Simple Kratix Promise Validator

This repo represents a simple Kratix promise validator. When supplied with a Kratix promise.yaml file, (containing an 
OpenAPI Schema structure) and an example user resource.yaml, (that requests the application of the promise) it will validate 
that the supplied values are correct.

## Why is this useful?

When a promise is installed in a platform k8s cluster, Kratix will validate that the user resource being applied meets the 
requirements of the promise schema and thus the contract.  This is great feedback for the user, but also can feel a bit late 
in the process.  If the promise has changed then the users of the promise want to know as early as possible what has changed
in the contract.

## Setup

```shell
python -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

##Execution

This simple script process two YAML files.  The first file represents the promise and the second file represents the
resource request.

```shell
python validate.py promise.yaml example-resource.yaml
```

## Example Output

#### Successful Validation
The following represents the output of a successful validation.

```
Extracted Schema:
 {
  "properties": {
    "spec": {
      "required": [
        "image"
      ],
      "properties": {
        "image": {
          "type": "string"
        },
        "service": {
          "properties": {
            "port": {
              "type": "integer",
              "enum": [
                8080,
                8081,
                8082,
                8083,
                8084,
                8085
              ],
              "default": 8080
            }
          },
          "type": "object"
        }
      },
      "type": "object"
    }
  },
  "type": "object"
}
Resource Data:
 {
  "apiVersion": "workshop.kratix.io/v1",
  "kind": "App",
  "metadata": {
    "name": "todo",
    "namespace": "default"
  },
  "spec": {
    "image": "syntasso/sample-todo:v0.1.0",
    "service": {
      "port": 8080
    }
  }
}
✅ Validation successful: The resource is valid according to the Promise schema.
```

#### Failed Validation
The following represents the output of a failed validation.

```
Extracted Schema:
 {
  "properties": {
    "spec": {
      "required": [
        "image"
      ],
      "properties": {
        "image": {
          "type": "string"
        },
        "service": {
          "properties": {
            "port": {
              "type": "integer",
              "enum": [
                8080,
                8081,
                8082,
                8083,
                8084,
                8085
              ],
              "default": 8080
            }
          },
          "type": "object"
        }
      },
      "type": "object"
    }
  },
  "type": "object"
}
Resource Data:
 {
  "apiVersion": "workshop.kratix.io/v1",
  "kind": "App",
  "metadata": {
    "name": "todo",
    "namespace": "default"
  },
  "spec": {
    "image": "syntasso/sample-todo:v0.1.0",
    "service": {
      "port": 9090
    }
  }
}
❌ Validation failed: 9090 is not one of [8080, 8081, 8082, 8083, 8084, 8085]
```