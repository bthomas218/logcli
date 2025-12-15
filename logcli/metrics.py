from collections.abc import Iterable
from typing import Any

class StatsAggregator():
    """Aggregates statistics from log records.

    Tracks total record count, counts by severity and service, latency statistics
    (min, max, average), and time range of processed records.

    Attributes
    - total (int): Total number of records processed.
    - by_severity (dict): Count of records for each severity level (lowercase keys).
    - by_service (dict): Count of records for each service (lowercase keys).
    - latency_count (int): Number of records with valid latency values.
    - latency_min (float | None): Minimum latency observed, or None if no latencies processed.
    - latency_max (float | None): Maximum latency observed, or None if no latencies processed.
    - latency_sum (float): Sum of all latency values.
    - start_time (datetime | None): Earliest timestamp observed, or None if no records processed.
    - end_time (datetime | None): Latest timestamp observed, or None if no records processed.
    """

    def __init__(self):
        """Initialize a new StatsAggregator with empty statistics."""
        self.total = 0
        self.by_severity = {}
        self.by_service = {}
        self.latency_count = 0
        self.latency_min = None
        self.latency_max = None
        self.latency_sum = 0
        self.start_time = None
        self.end_time = None

    def consume(self, rows: Iterable[dict[str, Any]]):
        """Process log records and update aggregate statistics.

        Iterates through the provided records and updates counts, latency stats,
        and time range. Severity and service values are normalized to lowercase.
        Only numeric latency values (int or float) are included in latency statistics.

        Parameters
        - rows (Iterable[dict]): An iterable of log record dictionaries. Each record
            should contain "severity", "service", and "timestamp" fields. Records may
            optionally contain a "latency_ms" field with numeric values.
        """
        for row in rows:
            self.total += 1
            
            severity = row.get("severity")
            if isinstance(severity, str):
                sev = severity.lower()
                self.by_severity[sev] = self.by_severity.get(sev, 0) + 1

            service = row.get("service")
            if isinstance(service, str):
                svc = service.lower()
                self.by_service[svc] = self.by_service.get(svc, 0) + 1

            timestamp = row.get("timestamp")
            self.start_time = timestamp if self.start_time is None else min(timestamp, self.start_time)
            self.end_time = timestamp if self.end_time is None else max(timestamp, self.end_time)

            latency = row.get("latency_ms")
            if isinstance(latency, (int, float)):
                self.latency_count += 1
                self.latency_sum += latency
                self.latency_min = latency if self.latency_min is None else min(latency, self.latency_min)
                self.latency_max = latency if self.latency_max is None else max(latency, self.latency_max)

    def to_dict(self):
        """Convert aggregated statistics to a dictionary.

        Returns
        - dict: A dictionary containing:
            - "total" (int): Total records processed.
            - "time_range" (dict): Contains "start" and "end" timestamps.
            - "service_counts" (dict): Count by service name (lowercase keys).
            - "severity_counts" (dict): Count by severity level (lowercase keys).
            - "latency_ms" (dict): Contains "count", "min", "max", and "avg".
                "avg" is None if no latency records were processed.
            - "error_rate" (float): Contains the error rate if logs with severity 'error' were present
        """
        avg = self.latency_sum / self.latency_count if self.latency_count else None
        error_rate = self.by_severity.get("error") / self.total if "error" in self.by_severity else None
        return {
            "total" : self.total,
            "time_range": {
                "start": self.start_time,
                "end": self.end_time,
            },
            "error_rate": error_rate,
            "service_counts": self.by_service,
            "severity_counts": self.by_severity,
            "latency_ms": {
                "count": self.latency_count,
                "min": self.latency_min,
                "max": self.latency_max,
                "avg": avg
            }
        }