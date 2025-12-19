# logcli

A lightweight CLI for analyzing and monitoring JSONL application logs. Designed for quick, local insights and simple alerting without running a full observability stack.

---

## Features

- Analyze structured JSONL logs
- Filter by time range, service, and severity
- Compute basic metrics (error rate, latency percentiles)
- Simple alerting via config file
- Human-readable or machine-readable output

---

## Log Format

`logcli` expects logs in **JSON Lines (JSONL)** format: one JSON object per line.

### Example Log Entry

```json
{
  "timestamp": "2025-01-01T12:34:56.789Z",
  "service": "payments-api",
  "severity": "ERROR",
  "message": "Payment failed",
  "latency_ms": 123,
  "trace_id": "abc-123",
  "extra": { "user_id": 42 }
}
```

### Supported Fields

Only the following fields are used during analysis:

- `timestamp` (ISO 8601, required)
- `service` (string, required)
- `severity` (string, required)
- `message` (string, required)
- `latency_ms` (number, optional)

All other fields are ignored.

---

## Configuration

Alerts and time windows are configured via a YAML file.

### Example Config File

```yaml
window_minutes: 5

alerts:
  - name: high_error_rate
    type: error_rate
    threshold: 0.05 # 5%

  - name: high_latency
    type: p95_latency
    threshold: 100 # milliseconds
```

### Configuration Fields

- `window_minutes`

  - Only logs within the last N minutes are considered

- `alerts`

  - A list of alert definitions
  - Alerts are evaluated on each run and printed to **stderr**

Each alert supports:

- `name`: Human-readable identifier
- `type`: Metric to evaluate
- `threshold`: Triggers when the computed value exceeds this number

### Supported Alert Types

- `error_rate` — percentage of logs with severity `ERROR`
- `p95_latency` — 95th percentile of `latency_ms`

---

## Requirements

- Python **>= 3.12**

---

## Installation

`logcli` is not published to PyPI yet. To install it locally, clone the repository and install in editable mode:

```bash
git clone https://github.com/bthomas218/logcli
cd logcli
pip install -e .
```

---

## Commands

### `analyze`

Analyze a static log file and print metrics.

```bash
logcli analyze path/to/log.jsonl
```

#### `analyze` Options

- `--since <timestamp>` — ISO 8601 start time
- `--until <timestamp>` — ISO 8601 end time
- `--severity <list>` — Space-separated severities (e.g. `ERROR WARN`)
- `--service <list>` — Space-separated service names
- `--output <format>` — Output format: `table` (default) or `json`

---

### `watch`

Continuously monitor a log file and emit alerts based on a config file.

```bash
logcli watch path/to/log.jsonl --config path/to/config.yml
```

#### `watch` Options

- `--config <path>` (required)

  - Path to the alert configuration file

Alerts are written to **stderr** so they can be captured separately from standard output.

---

## Example Workflow

```bash
# Analyze recent errors in payments services
logcli analyze logs.jsonl \
  --since 2025-01-01T12:00:00Z \
  --severity ERROR \
  --service payments-api

# Watch logs and trigger alerts
logcli watch logs.jsonl --config config.yml
```

---

## Notes

- Timestamps must be valid ISO 8601 strings
- Log files are processed sequentially; very large files may impact performance
- Intended for local usage and lightweight monitoring

---

## License

MIT
