import unittest
import sys
import json
from datetime import datetime
from pathlib import Path
from logcli.analyze import analyze

class Args:
    def __init__(self,
                 log: str, 
                 since: datetime = None,
                 until: datetime = None,
                 service: str = None,
                 severity: str = None,
                 output: str = None):
        self.log = log
        self.since = since
        self.until = until
        self.service = service
        self.severity = severity
        self.output = output
        self.verbose = False
        

class TestAnalyzeFunction(unittest.TestCase):

    def test_blank_json(self):
        
        args = Args('./tests/blank.jsonl', output="json")
        expected_result = {
            'total': 0, 
            'time_range': 
                {'start': None, 
                 'end': None}, 
            'error_rate': None, 
            'service_counts': {}, 
            'severity_counts': {}, 
            'latency_ms': {'count': 0, 'min': None, 'max': None, 'avg': None, 'p95': None},
            "error_info": {
                "parse_errors": 0,
                "invalid_records": 0
                }
            }
        

        stdout = sys.stdout
        output = Path('output.jsonl')

        try:
            with output.open('w') as f:
                sys.stdout = f
                analyze(args)
        finally:
            sys.stdout = stdout

        try:
            with output.open('r', encoding='utf-8') as f:
                actual_result = json.load(f)
                self.assertEqual(actual_result, expected_result)
        finally:
            output.unlink()

        
        
        


    