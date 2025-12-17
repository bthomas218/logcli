import json
from datetime import datetime

def output_table(stats, error_info):
    return f"""Summary:
  Total lines: {stats["total"]}
  Time range: {stats["time_range"]["start"]} -> {stats["time_range"]["end"]}
  Error rate: {stats["error_rate"]}

By severity:
  {"\n  ".join(f'{k.upper()}: {v}' for k, v in stats["severity_counts"].items())}

By service:
  {"\n  ".join(f'{k}: {v}' for k, v in stats["service_counts"].items())}

Latency (ms):
  {"\n  ".join(f'{k}: {v}' for k, v in stats["latency_ms"].items())}

Error Info:
  Parse Errors: {error_info.parse_errors}
  Invalid records (missing fields): {error_info.invalid_records}"""

def output_json(stats, error_info):
    if stats["time_range"]["start"]:
        stats["time_range"]["start"] = stats["time_range"]["start"].isoformat()
    if stats["time_range"]["end"]:
        stats["time_range"]["end"] = stats["time_range"]["end"].isoformat()
    stats["error_info"] = {
        "parse_errors": error_info.parse_errors,
        "invalid_records": error_info.invalid_records
    }
    json_string = json.dumps(stats, indent=4)
    return json_string