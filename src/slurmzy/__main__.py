#!/usr/bin/env python3

import argparse

import slurmzy


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="slurmzy",
        usage="slurmzy <command> <options>",
        description="Slurm wrapper script",
    )

    parser.add_argument("--version", action="version", version=slurmzy.__version__)

    subparsers = parser.add_subparsers(title="Available commands", help="", metavar="")

    subparser_run = subparsers.add_parser(
        "run",
        help="Submit job to slurm",
        usage="slurmzy run [options] <memory in GB> <name> <command>",
        description="slurmzy run [options] <ram in GB> <name> <command>",
    )
    subparser_run.add_argument("--dry_run", action="store_true", help="Do not submit job. Print the script that would be submitted")
    subparser_run.add_argument("-t", "--time", type=float, help="Time limit in hours [%(default)s]", default=1, metavar="FLOAT")
    subparser_run.add_argument('ram', type=float, help='RAM limit in GB (FLOAT)')
    subparser_run.add_argument('name', type=str, help='Name of the job')
    subparser_run.add_argument('command', nargs=argparse.REMAINDER, help='Command to be run')
    subparser_run.set_defaults(func=slurmzy.sbatch.run)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
