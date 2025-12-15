from pathlib import Path
import json
import sys
from datetime import datetime
from abc import ABC, abstractmethod

"""Reader classes for log input sources.

This module provides an abstract :class:`LogReader` and concrete
implementations :class:`FileLogReader` and :class:`StdinLogReader`.

Usage:
- Instantiate one of the concrete readers (e.g. ``FileLogReader(Path('x.jsonl'), True)``).
- Iterate the instance to receive validated log records (each is a ``dict``).
- When iteration completes, the iterator's ``StopIteration.value`` contains
    a summary ``dict`` with keys ``parse_errors`` and ``invalid_records``.

Each reader maintains counters on the instance: ``parse_errors`` and
``invalid_records``. Set ``verbose=True`` to print parse/validation errors as
they occur.
"""

REQUIRED_FIELDS = {"severity", "timestamp", "service", "message"}

class LogReader(ABC):
    """Abstract base class for log readers.

    Subclasses must implement ``__iter__`` to yield validated log records.

    Attributes
    - parse_errors (int): Number of JSON parse errors encountered.
    - invalid_records (int): Number of records that failed validation.
    - verbose (bool): Whether to print errors as they occur.
    """

    def __init__(self, verbose: bool):
        self.parse_errors = 0
        self.invalid_records = 0
        self.verbose = verbose

    @abstractmethod
    def __iter__(self): # must be implemented by base classes
        pass

class FileLogReader(LogReader):
    """Reader for JSON Lines files (``.jsonl``).

    Create with ``FileLogReader(file: Path, verbose: bool)`` and iterate the
    instance to obtain validated records. Records yielded have their
    ``timestamp`` converted to ``datetime`` objects. After iteration,
    ``StopIteration.value`` holds a summary dict: ``{"parse_errors": .., "invalid_records": ..}``.
    """

    def __init__(self, file: Path, verbose: bool):
        super().__init__(verbose)
        self.file = file

    def __iter__(self):
        yield from self._read_file()

    def _read_file(self):
        """Generator that yields validated records from ``self.file``.

        Yields validated record ``dict`` objects. Increments
        ``self.parse_errors`` on JSON parse failures and
        ``self.invalid_records`` on validation failures. If ``self.verbose`` is
        true, errors are printed as they occur.

        When the generator is exhausted, it returns a summary dict with keys
        ``parse_errors`` and ``invalid_records`` (available as
        ``StopIteration.value``).
        """

        file = self.file
        verbose = self.verbose

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
                        self.parse_errors += 1
                        if verbose:
                            print(f"Error decoding JSON: {e}")
                    except ExceptionGroup as eg:
                        self.invalid_records += 1
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

class StdinLogReader(LogReader):
    def __init__(self, verbose: bool):
        """Reader that yields validated records from standard input.

        Instantiate with ``StdinLogReader(verbose: bool)`` and iterate the object
        to receive validated records. Counters and return semantics are the same
        as :class:`FileLogReader`.
        """
        super().__init__(verbose)

    def __iter__(self):
        yield from self._read_stdin()

    def _read_stdin(self):
        """Generator that yields validated records read from ``sys.stdin``.

        Behavior mirrors :meth:`FileLogReader._read_file`: yields validated
        ``dict`` records, updates ``self.parse_errors`` and
        ``self.invalid_records``, and returns a summary dict on completion
        (available via ``StopIteration.value``).
        """

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
                self.parse_errors += 1
                if self.verbose:
                    print(f"Error decoding JSON on line: {e}")
            except ExceptionGroup as eg:
                self.invalid_records += 1
                if self.verbose:
                    print(f"{eg} on line number {line_number}")
                    for i, exc in enumerate(eg.exceptions):
                        print(f"\tSub-exception {i+1}: {type(exc).__name__}: {exc}")
        line_number += 1
    


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