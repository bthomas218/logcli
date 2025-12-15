from collections.abc import Iterable
from typing import Any
from datetime import datetime

Row = dict[str, Any]

def _filter_by_field(
    data: Iterable[Row],
    values: set[str],
    field: str,
):
    if not values:
        yield from data
        return

    for row in data:
        if row.get(field).lower() in values:
            yield row

def filter_by_service(data: Iterable[Row], services: set[str]):
    yield from _filter_by_field(data, services, "service")

def filter_by_severity(data: Iterable[Row], severities: set[str]):
    yield from _filter_by_field(data, severities, "severity")

def filter_since(data: Iterable[Row], timestamp: datetime):
    if not timestamp:
        yield from data
        return
    
    for row in data:
        if row.get("timestamp") >= timestamp:
            yield row

def filter_until(data: Iterable[Row], timestamp: datetime):
    if not timestamp:
        yield from data
        return
    
    for row in data:
        if row.get("timestamp") <= timestamp:
            yield row
