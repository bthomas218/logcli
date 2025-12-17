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

    # Get the configuration
    raw = _parse_yml(Path(args.config).resolve())
    cfg = _validate_cfg(raw)
    
    # Read the log json
    reader = FileLogReader(Path(args.log).resolve(), args.verbose) if args.log else StdinLogReader(args.verbose)

    # Apply filters
    data = reader
    duration = datetime.now(timezone.utc) - timedelta(minutes=cfg.window_minutes)
    data = filter_since(data, duration)
    
    # Aggregate
    agg = StatsAggregator()
    agg.consume(data)
    stats = agg.to_dict()

    # Check to see if alerts fired
    messages = _eval_alerts(stats, cfg)
    if messages: 
        for msg in messages:
            print(f"ALERT: {msg}", file=sys.stderr)
        exit(1)
    else:
        print("OK", file=sys.stderr)
    

@dataclass
class AlertRule:
    """
    Represents an alert rule in config file

    :params
    """
    name: str
    type: str
    threshold: float | int

@dataclass
class WatchConfig:
    """
    Represents the watch configuration
    """
    window_minutes: int
    alerts: list[AlertRule]


def _parse_yml(file: Path):
    """
    Parses a yaml file 
    
    :param file: The yml file to parse
    :type file: Path
    """
    try:
        with file.open(mode='r', encoding="utf-8") as f:
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

def _validate_cfg(cfg: dict | None) -> WatchConfig:
    """
    Validates a possible config object against the schema
    
    :param cfg: A possible config object to validate
    :type cfg: dict | None
    :return: The configuration object
    :rtype: WatchConfig
    """
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

def _eval_alerts(stats: dict, cfg: WatchConfig) -> list[str]:
    """
    Evaluates if any alerts went off
    
    :param stats: aggregation stats to check
    :type stats: dict
    :param cfg: Configuration rules
    :type cfg: WatchConfig
    :return: A list of messages of alerts that went off
    :rtype: list[str]
    """

    messages = []
    for rule in cfg.alerts:

        match(rule.type):
            case "error_rate":
                er = stats["error_rate"]
                if er is None:
                    continue
                if er >= rule.threshold:
                    messages.append(f"[{rule.name}] error_rate={er*100:.2f}% > threshold={rule.threshold:.2f}%")
            case "p95_latency":
                er = stats["latency_ms"].get("p95")
                if er is None:
                    continue
                if er > rule.threshold:
                    messages.append(f"[{rule.name}] p95_latency={er:.2f}ms > threshold={rule.threshold:.2f}ms")
            case _:
                continue
    
    return messages



