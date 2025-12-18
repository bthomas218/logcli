"""Filtering helpers for streamed log records.

    This module provides small, composable generator-based filters that accept an
    iterable of log rows (``Row``) and yield rows that match the requested
    criteria. Filters are designed to be chained, e.g.::

        data = FileLogReader(...)
        data = filter_since(data, since_ts)
        data = filter_by_service(data, services)

    Types
    - ``Row``: alias for ``dict[str, Any]`` representing a parsed log record.
"""

from collections.abc import Iterable
from typing import Any
from datetime import datetime

Row = dict[str, Any]


def _filter_by_field(
        data: Iterable[Row],
        values: set[str],
        field: str,
):
    """Yield rows whose ``field`` value (lowercased) is present in ``values``.

        Parameters
        - data: Iterable of log rows to filter.
        - values: set of lowercase strings to match against the field value. If
          empty, the input ``data`` is yielded unchanged.
        - field: The key in each row to compare (e.g. "service" or "severity").

        Yields
        - Row: rows that match one of the provided values.
    """
    if not values:
        yield from data
        return

    for row in data:
        value = row.get(field)
        if value is None:
            continue
        if str(value).lower() in values:
            yield row


def filter_by_service(data: Iterable[Row], services: set[str]):
    """Filter rows by the ``service`` field.

        Parameters
        - data: Iterable of log rows.
        - services: set of lowercase service names to allow. If empty, all rows
          are yielded.

        Yields
        - Row: rows whose ``service`` value is in ``services``.
    """
    yield from _filter_by_field(data, services, "service")


def filter_by_severity(data: Iterable[Row], severities: set[str]):
    """Filter rows by the ``severity`` field.

        Parameters
        - data: Iterable of log rows.
        - severities: set of lowercase severity strings to allow. If empty, all
          rows are yielded.

        Yields
        - Row: rows whose ``severity`` value is in ``severities``.
    """
    yield from _filter_by_field(data, severities, "severity")


def filter_since(data: Iterable[Row], timestamp: datetime):
    """Yield rows with ``timestamp`` >= given ``timestamp``.

        Parameters
        - data: Iterable of log rows. Each row must have a ``timestamp`` value
          that is a ``datetime`` (the readers convert ISO strings to datetimes).
        - timestamp: If falsy, the input ``data`` is yielded unchanged.

        Yields
        - Row: rows whose ``timestamp`` is greater than or equal to ``timestamp``.
    """
    if not timestamp:
        yield from data
        return

    for row in data:
        row_ts = row.get("timestamp")
        if row_ts is None:
            continue
        if row_ts >= timestamp:
            yield row


def filter_until(data: Iterable[Row], timestamp: datetime):
    """Yield rows with ``timestamp`` <= given ``timestamp``.

        Parameters
        - data: Iterable of log rows. Each row must have a ``timestamp`` value
          that is a ``datetime``.
        - timestamp: If falsy, the input ``data`` is yielded unchanged.

        Yields
        - Row: rows whose ``timestamp`` is less than or equal to ``timestamp``.
    """
    if not timestamp:
        yield from data
        return

    for row in data:
        row_ts = row.get("timestamp")
        if row_ts is None:
            continue
        if row_ts <= timestamp:
            yield row
