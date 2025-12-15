import argparse
from pathlib import Path
from reader import FileLogReader, StdinLogReader

# Definition for main CLI
parser = argparse.ArgumentParser(prog="logcli", description="A tool that analyzes logs")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

# Defintion for subcommands
subparsers = parser.add_subparsers(dest='command', help='Available commands')


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

# Function used by analzye command
def analzye(args):
    _print_verbose(args)
    data = FileLogReader(Path(args.log).resolve(), args.verbose) if args.log else StdinLogReader(args.verbose)
    for row in data:
        print(row)
    print(f"Error Info:\n\tParse Errors: {data.parse_errors}\n\tInvalid Records: {data.invalid_records}")
    
    

analyze_parser = subparsers.add_parser('analyze', help='perform analysis on a log file')
analyze_parser.add_argument("log", nargs='?', help="The name/path of the logs to analyze",)
analyze_parser.add_argument("--since", type=str, help="Filter logs since this timestamp, input as a string")
analyze_parser.add_argument("--until", type=str, help="Filter logs up until this timestamp, input as a string")
analyze_parser.add_argument("--severity", nargs="+", help="Filter logs that contain these levels of severity")
analyze_parser.add_argument("--service", nargs="+", help="Filter logs that come from these services")
analyze_parser.add_argument("--output", choices=["table", "json"], help="Format analysis according to this output, defaults to table")
analyze_parser.set_defaults(function=analzye)




# Run the program
args = parser.parse_args()
if hasattr(args, 'function'):
    args.function(args)
else:
    parser.print_help()