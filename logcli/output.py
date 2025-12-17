# TODO: json renders

def outputTable(stats, error_info):
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
  Invalid records (missing fields): {error_info.invalid_records}
"""