from .cli import args, parser

def main():
    if hasattr(args, 'function'):
        args.function(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()