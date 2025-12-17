import yaml
from pathlib import Path
from datetime import datetime
from reader import FileLogReader, StdinLogReader
from filters import filter_until, filter_since
from metrics import *


ALERT_TYPES = ["error_rate", "p95_latency"]

def watch(args):
    data = _parse_cfg(Path(args.config).resolve())
    _validate_cfg(data)
    print(data)


def _parse_cfg(cfg: Path):
    try:
        with cfg.open(mode='r', encoding="utf-8") as f:
             data = yaml.safe_load(f) 
             return data
    except yaml.YAMLError as e:
         print("Error while parsing YAML file")
         exit(2)
    except FileNotFoundError:
        print("Error: config file not found")
        exit(2)

def _validate_cfg(cfg: dict):
    if not isinstance(cfg["window_minutes"], int):
        print("Error: Config file is missing or invalid 'window_minutes' field")
        exit(2)
    if not isinstance(cfg['alerts'], list):
        print("Error: Config file is missing or invalid 'alerts' field")
        exit(2)

    for alert in cfg['alerts']:
        if not isinstance(alert["name"], str):
            print("Error: An alert is missing or has an invalid 'name' field")
            exit(2)
        alert_name = alert["name"]
        if alert["type"] not in ALERT_TYPES:
            print(f"Error: Alert '{alert_name}' has invalid type")
            exit(2)
        if not isinstance(alert["threshold"], int):
            print(f"Error: Alert '{alert_name}' has missing or invalid 'threshold' field")
            exit(2)
