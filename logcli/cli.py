import argparse

# Definition for main CLI
parser = argparse.ArgumentParser(prog="logcli", description="A tool that analyzes logs")

# Defintion for subcommands
subparsers = parser.add_subparsers(dest='command', help='Available commands')

# Defintion for the analyze command
def analzye(args):
    print(f"Analyzing log: {args.log}")
    if args.since:
        print(f"Since time: {args.since}")
    if args.until:
        print(f"Until time: {args.until}")
    if args.severity:
        print(f"With severity: {args.severity}")
    if args.service:
        print(f"From services: {args.service}")
    if args.output:
        print(f"With output: {args.output}")
    else:
        print(f"With output: table")
    

analyze_parser = subparsers.add_parser('analyze', help='perform analysis on a log file')
analyze_parser.add_argument("log", help="The name/path of the logs to analyze")
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