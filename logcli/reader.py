# TODO: validate input data
from pathlib import Path
import json
import sys
from datetime import datetime


REQUIRED_FIELDS = {"severity", "timestamp", "service", "message"}

def read_file(file: Path):
    """
    Reads data from a jsonl file
    
    :param file: Path to the jsonl file to read
    :type file: Path
    """

    errorinfo = {
        "parse_errors": 0,
        "invalid_records": 0
    }

    if file.suffix != ".jsonl":
        print(f"Error: unsupported file type '{file.suffix}'")
        exit(1)

    try:
        with file.open(mode='r', encoding='utf-8') as f:
            for line in f:
                try:
                    json_obj = json.loads(line.strip())
                    validate_obj(json_obj)
                    yield json_obj
                except json.JSONDecodeError as e:
                    errorinfo["parse_errors"] += 1
                    print(f"Error decoding JSON: {e}")
                    continue
                except ExceptionGroup as eg:
                    errorinfo["invalid_records"] += 1
                    print(eg)
                    for i, exc in enumerate(eg.exceptions):
                        print(f"  Sub-exception {i+1}: {type(exc).__name__}: {exc}")
                    continue
    except FileNotFoundError:
        print(f"Error: The file '{file}'  was not found")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

    return errorinfo

def read_stdin():
    """
    Reads json data from stdin
    """

    errorinfo = {
        "parse_errors": 0,
        "invalid_records": 0
    }

    for line in sys.stdin:
        processed_line = line.rstrip()
        if processed_line == 'Exit':
            break
        try:
            json_obj = json.loads(processed_line)
            validate_obj(json_obj)
            yield json_obj
        except json.JSONDecodeError as e:
            errorinfo["parse_errors"] += 1
            print(f"Error decoding JSON on line: {e}")
            continue
        except ExceptionGroup as eg:
            errorinfo["invalid_records"] += 1
            print(eg)
            for i, exc in enumerate(eg.exceptions):
                print(f"  Sub-exception {i+1}: {type(exc).__name__}: {exc}")
            continue
    
    return errorinfo


def validate_obj(obj: dict) -> dict:
    """
    Verfies the required fields are in the object and converts timestamp strings to timestamp objects
    
    :param obj: The object to validate
    :type obj: dict

    Returns:
        dict: the object with the data validated if it passes the checks
    """
    errors = []
    for field in REQUIRED_FIELDS: 
        if field not in obj:
            errors.append(KeyError(f"log is missing required field: {field}"))
            continue
        if field == "timestamp":
            try:
                timestamp = datetime.fromisoformat(obj.get("timestamp"))
                obj["timestamp"] = timestamp
            except ValueError:
                errors.append(ValueError(f"log has invalid timestamp"))

    if errors:
        raise ExceptionGroup("Validation error:", errors)
    
    return obj