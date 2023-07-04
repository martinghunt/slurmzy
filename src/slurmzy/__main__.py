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

    # ------------------------ run --------------------------------------------
    subparser_run = subparsers.add_parser(
        "run",
        help="Submit job to slurm",
        usage="slurmzy run [options] <memory in GB> <name> <command>",
        description="Submit job to slurm",
    )
    subparser_run.add_argument(
        "--norun",
        action="store_true",
        help="Do not submit job. Print the script that would be submitted",
    )
    subparser_run.add_argument(
        "--array_start",
        type=int,
        help="Start index of job array",
        metavar="INT",
    )
    subparser_run.add_argument(
        "--array_end",
        type=int,
        help="End index of job array",
        metavar="INT",
    )
    subparser_run.add_argument(
        "--array_limit",
        type=int,
        help="Max array elements allowed to run [%(default)s]",
        default=10,
        metavar="INT",
    )
    subparser_run.add_argument(
        "-c",
        "--cpus",
        type=int,
        help="Number of cpus [%(default)s]",
        default=1,
        metavar="INT",
    )
    subparser_run.add_argument(
        "-q",
        "--queue",
        help="Queue ('partition') to use instead of default",
        metavar="QUEUE_NAME",
    )
    subparser_run.add_argument(
        "-t",
        "--time",
        type=float,
        help="Time limit in hours [%(default)s]",
        default=1,
        metavar="FLOAT",
    )
    subparser_run.add_argument("ram", type=float, help="RAM limit in GB (FLOAT)")
    subparser_run.add_argument("name", type=str, help="Name of the job")
    subparser_run.add_argument(
        "command", nargs=argparse.REMAINDER, help="Command to be run"
    )
    subparser_run.set_defaults(func=slurmzy.sbatch.run)

    # ------------------------ ostats -----------------------------------------
    subparser_ostats = subparsers.add_parser(
        "ostats",
        help="Gather stats from .o files of finished jobs",
        usage="slurmzy ostats [options] <list of .o files>",
        description="Gather stats from .o files of finished jobs",
    )
    subparser_ostats.add_argument(
        "filenames", nargs="+", help="Name(s) of .o file(s)"
    )
    subparser_ostats.add_argument(
        "-a", "--all_columns", action="store_true", help="Output all columns"
    )
    subparser_ostats.add_argument(
        "-f", "--fails", action="store_true", help="Output only failed jobs"
    )
    subparser_ostats.add_argument(
        "--time_units", choices=["s", "m", "h"], help="Time units to report, h (hours), m (minutes), s (seconds) [%(default)s]", default="h", metavar="s|m|h",
    )
    subparser_ostats.set_defaults(func=slurmzy.job_stats.parse_o_files)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
