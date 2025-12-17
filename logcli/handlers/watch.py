import yaml
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from reader import FileLogReader, StdinLogReader
from dataclasses import dataclass
from filters import filter_since
from metrics import *


ALERT_TYPES = ["error_rate", "p95_latency"]

def watch(args):
    raw = _parse_cfg(Path(args.config).resolve())
    cfg = _validate_cfg(raw)
    duration = datetime.now(timezone.utc) - timedelta(minutes=cfg.window_minutes)
    
    reader = FileLogReader(Path(args.log).resolve(), args.verbose) if args.log else StdinLogReader(args.verbose)

    data = reader
    
    data = filter_since(data, duration)
    
    agg = StatsAggregator()
    agg.consume(data)
    stats = agg.to_dict()

    print(stats)

@dataclass
class AlertRule:
    name: str
    type: str
    threshold: float | int

@dataclass
class WatchConfig:
    window_minutes: int
    alerts: list[AlertRule]


def _parse_cfg(cfg: Path):
    try:
        with cfg.open(mode='r', encoding="utf-8") as f:
            data = yaml.safe_load(f) 
            return data
    except yaml.YAMLError as e:
         print("Error while parsing YAML file",  file=sys.stderr)
         exit(2)
    except FileNotFoundError:
        print("Error: config file not found", file=sys.stderr)
        exit(2)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        exit(1)

def _validate_cfg(cfg: dict | None):
    if not isinstance(cfg, dict):
        print("Error: Config is missing", file=sys.stderr)
        exit(2)
    if not isinstance(cfg.get("window_minutes"), int):
        print("Error: Config file is missing or invalid 'window_minutes' field", file=sys.stderr)
        exit(2)
    if not isinstance(cfg.get("alerts"), list):
        print("Error: Config file is missing or invalid 'alerts' field", file=sys.stderr)
        exit(2)

    alerts = []

    for alert in cfg.get("alerts"):
        if not isinstance(alert.get("name"), str):
            print("Error: An alert is missing or has an invalid 'name' field", file=sys.stderr)
            exit(2)
        alert_name = alert.get("name")
        if alert.get("type") not in ALERT_TYPES:
            print(f"Error: Alert '{alert_name}' has invalid type", file=sys.stderr)
            exit(2)
        if not isinstance(alert.get("threshold"), int | float):
            print(f"Error: Alert '{alert_name}' has missing or invalid 'threshold' field", file=sys.stderr)
            exit(2)
        alert = AlertRule(alert_name, alert.get("type"), alert.get("threshold"))
        alerts.append(alert)
    
    return WatchConfig(cfg.get("window_minutes"), alerts)
