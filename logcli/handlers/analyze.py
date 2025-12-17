from pathlib import Path
from datetime import datetime
from reader import FileLogReader, StdinLogReader
from filters import filter_by_service, filter_by_severity, filter_until, filter_since
from metrics import *
from output import *

# Verbose output for analyze command
def _print_verbose(args):
    if not args.verbose:
        return
    output = args.output or "table"

    messages = [
        f"Analyzing log: {args.log}" if args.log else "Analyzing logs from stdin",
        *((f"Since time: {args.since}",) if args.since else ()),
        *((f"Until time: {args.until}",) if args.until else ()),
        *((f"With severity: {args.severity}",) if args.severity else ()),
        *((f"From services: {args.service}",) if args.service else ()),
        f"With output: {output}",
    ]

    print("\n".join(messages))

# process and validate user input for analyze command
def _process_args(args):
    if args.since:
        try:
            args.since = datetime.fromisoformat(args.since)
        except ValueError:
            print("Error: Invalid timestamp for since flag")
            exit(1)
    if args.until:
        try:
            args.until = datetime.fromisoformat(args.until)
        except ValueError:
            print("Error: Invalid timestamp for until flag")
            exit(1)
    if args.service:
        args.service = {service.lower() for service in args.service}
    if args.severity:
        args.severity = {severity.lower() for severity in args.severity}
    args.output = args.output if args.output else "table"

# Function used by analyze command
def analyze(args):

    _process_args(args)
    _print_verbose(args)

    # Create reader object
    reader = FileLogReader(Path(args.log).resolve(), args.verbose) if args.log else StdinLogReader(args.verbose)
    
    # Apply filters
    data = reader
    data = filter_by_service(data, args.service)
    data = filter_by_severity(data, args.severity)
    data = filter_since(data, args.since)
    data = filter_until(data, args.until)

    agg = StatsAggregator()
    agg.consume(data)
    stats = agg.to_dict()
    
    # Print output to stdout
    match args.output:
        case "table":
            print(output_table(stats, reader))
        case "json":
            print(output_json(stats, reader))
        case _:
            print("Error: Invalid output format")
            exit(1)
    
    