from streamstock_collector.const import *
import streamstock_collector
import argparse


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     prog=PROG)

    subparser = parser.add_subparsers(help='list of commands', dest='command')

    run_parser = subparser.add_parser('run', help=RUN_COMMAND_HELP)

    args = parser.parse_args()

    if args.command == 'run':
        streamstock_collector.init()


if __name__ == '__main__':
    main()
