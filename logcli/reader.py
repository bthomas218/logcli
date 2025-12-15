# TODO: validate input data
from pathlib import Path
import json
import sys

def read_file(file: Path):
    """
    Reads data from a jsonl file
    
    :param file: Path to the jsonl file to read
    :type file: Path
    """
    data = []
    if file.suffix != ".jsonl":
        print(f"Error: unsupported file type '{file.suffix}'")
        exit(1)
    try:
        with file.open(mode='r', encoding='utf-8') as f:
            for line in f:
                try:
                    json_obj = json.loads(line.strip())
                    data.append(json_obj)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    continue
    except FileNotFoundError:
        print(f"Error: The file '{file}'  was not found")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
    return data

def read_stdin():
    """
    Reads data from stdin
    """
    data = []
    for line in sys.stdin:
        processed_line = line.rstrip()
        if processed_line == 'Exit':
            break
        try:
            json_obj = json.loads(processed_line)
            data.append(json_obj)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON on line: {e}")
            continue
    return data