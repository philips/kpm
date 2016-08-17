#!/usr/bin/env python
import argparse
from kpm.commands import all_commands


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command help')
    for _, commandClass in all_commands.iteritems():
        commandClass.add_parser(subparsers)
    return parser


def cli():
    parser = get_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (argparse.ArgumentTypeError, argparse.ArgumentError) as e:
        parser.error(e.message)
