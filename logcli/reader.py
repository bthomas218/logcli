from pathlib import Path
import json
import sys
from datetime import datetime


REQUIRED_FIELDS = {"severity", "timestamp", "service", "message"}

def read_file(file: Path, verbose = False):
    """Read records from a JSON Lines (.jsonl) file as a generator.

        This function yields one parsed JSON object per valid input line. Each
        yielded object has its ``timestamp`` field converted from an ISO-8601
        string to a :class:`datetime.datetime` object by :func:`validate_obj`.

        Parameters
        - file (Path): Path to the input ``.jsonl`` file.
        - verbose (bool): If True, print parse and validation errors as they occur.

        Yields
        - dict: A validated record (with ``timestamp`` converted to ``datetime``).

        Returns
        - dict: A summary dictionary with keys ``parse_errors`` and
            ``invalid_records`` when the generator is exhausted (accessible as
            ``StopIteration.value``).
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
            line_number = 0
            for line in f:
                try:
                    json_obj = json.loads(line.strip())
                    validate_obj(json_obj)
                    yield json_obj
                except json.JSONDecodeError as e:
                    errorinfo["parse_errors"] += 1
                    if verbose:
                        print(f"Error decoding JSON: {e}")
                except ExceptionGroup as eg:
                    errorinfo["invalid_records"] += 1
                    if verbose:
                        print(f"{eg} on line number {line_number}")
                        for i, exc in enumerate(eg.exceptions):
                            print(f"\tSub-exception {i+1}: {type(exc).__name__}: {exc}")
                line_number += 1

    except FileNotFoundError:
        print(f"Error: The file '{file}' was not found")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

    return errorinfo

def read_stdin(verbose = False):
    """Read JSON records from standard input as a generator.

        Reads lines from ``sys.stdin``, yielding one parsed JSON object per valid
        line. Each yielded object has its ``timestamp`` field converted to a
        :class:`datetime.datetime` by :func:`validate_obj`.

        Parameters
        - verbose (bool): If True, print parse and validation errors as they occur.

        Yields
        - dict: A validated record (with ``timestamp`` converted to ``datetime``).

        Returns
        - dict: A summary dictionary with keys ``parse_errors`` and
            ``invalid_records`` when the generator is exhausted (accessible as
            ``StopIteration.value``).
    """

    errorinfo = {
        "parse_errors": 0,
        "invalid_records": 0
    }

    line_number = 0
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
            if verbose:
                print(f"Error decoding JSON on line: {e}")
        except ExceptionGroup as eg:
            errorinfo["invalid_records"] += 1
            if verbose:
                print(f"{eg} on line number {line_number}")
                for i, exc in enumerate(eg.exceptions):
                    print(f"\tSub-exception {i+1}: {type(exc).__name__}: {exc}")
        line_number += 1
    
    return errorinfo


def validate_obj(obj: dict) -> dict:
    """Validate a single log object and normalize its fields.

        Validation performed:
        - Ensures all required fields (``severity``, ``timestamp``, ``service``,
            ``message``) are present.
        - Converts the ``timestamp`` field from an ISO-8601 string to a
            :class:`datetime.datetime` object.

        Parameters
        - obj (dict): The parsed JSON object to validate.

        Returns
        - dict: The same object with normalized fields (``timestamp`` as
            ``datetime``) if validation succeeds.

        Raises
        - ExceptionGroup: If one or more validation errors occur. Each sub-exception
            will be either ``KeyError`` for missing fields or ``ValueError`` for an
            invalid timestamp.
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