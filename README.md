# logcli

Log Analyzer &amp; Monitoring CLI

## Planned Usage

### Log format

```bash
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

#### fields

- timestamp (ISO 8601)
- service
- severity
- latency_ms (Optional)
- message

All other fields will be ignored

### Input format

JSON Lines (.jsonl): one JSON object per line.
stdin: one JSON object per line

### Commands

#### `analyze`

```bash
logcli analyze path/to/log.jsonl
```

#### flags

- `--since`, `--until` (string timestamps in ISO 8601)
- `--severity` (space separated list)
- `--service` (space seperated list)
- `--output` in `["table", "json"]`
