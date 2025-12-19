import unittest
import sys
import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from logcli.watch import watch

class Args:
    def __init__(self,
                 log: str, 
                 config: str,):
        self.log = log
        self.config = config
        self.verbose = False
        

class TestWatchFunction(unittest.TestCase):

    def test_blank_json(self):
        
        args = Args(log='./tests/blank.jsonl', config="./tests/testcfg.yml")
        expected_result = "OK\n"
        

        stderr = sys.stderr
        output = Path('output.txt')

        try:
            with output.open('w') as f:
                sys.stderr = f
                watch(args)
        finally:
            sys.stderr = stderr

        try:
            with output.open('r', encoding='utf-8') as f:
                actual_result = f.read()
                self.assertEqual(expected_result, actual_result)
        finally:
            output.unlink()

    def test_alerts(self):
        # create recent log entries within the watch window to trigger alerts
        input = Path('input.jsonl')
        with input.open('w', encoding='utf-8') as f:
            # generate multiple error entries with latency > 100ms
            data_list = ({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "test-service",
                "severity": "ERROR",
                "message": "this is for a test",
                "latency_ms": 101
            } for _ in range(100))

            for item in data_list:
                json_line = json.dumps(item)
                f.write(json_line + os.linesep)

        args = Args(log=str(input), config="./tests/testcfg.yml")

        stderr = sys.stderr
        output = Path('output.txt')

        try:
            with output.open('w') as f:
                sys.stderr = f
                # watch() will call exit(1) on alerts -> raises SystemExit
                with self.assertRaises(SystemExit) as cm:
                    watch(args)
                self.assertEqual(cm.exception.code, 1)
        finally:
            sys.stderr = stderr

        try:
            with output.open('r', encoding='utf-8') as f:
                actual_result = f.read()
                # both error-rate and p95 latency alerts should appear
                self.assertIn("ALERT: [high_error_rate]", actual_result)
                self.assertIn("ALERT: [high_latency]", actual_result)
        finally:
            output.unlink()
            input.unlink()