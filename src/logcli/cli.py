import argparse
from .analyze import analyze
from .watch import watch


# Definition for main CLI
parser = argparse.ArgumentParser(prog="logcli", description="A tool that analyzes logs")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

# Defintion for subcommands
subparsers = parser.add_subparsers(dest='command', help='Available commands')

# Analyze command
analyze_parser = subparsers.add_parser('analyze', help='perform analysis on a log file')
analyze_parser.add_argument("log", nargs='?', help="The name/path of the logs to analyze",)
analyze_parser.add_argument("--since", type=str, help="Filter logs since this timestamp, input as a string")
analyze_parser.add_argument("--until", type=str, help="Filter logs up until this timestamp, input as a string")
analyze_parser.add_argument("--severity", nargs="+", help="Filter logs that contain these levels of severity")
analyze_parser.add_argument("--service", nargs="+", help="Filter logs that come from these services")
analyze_parser.add_argument("--output", choices=["table", "json"], help="Format analysis according to this output, defaults to table")
analyze_parser.set_defaults(function=analyze)

# Watch command
watch_parser = subparsers.add_parser('watch', help="Evaluates log data over a sliding time window and triggers alerts based on rules defined in a config file")
watch_parser.add_argument("log", nargs='?', help="The name/path of the logs to watch")
watch_parser.add_argument("--config", "-c", required=True, help="The name/path of the config file")
watch_parser.set_defaults(function=watch)

args = parser.parse_args()