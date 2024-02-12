import os
import subprocess


def convert_ram(ram_in_gb):
    if int(ram_in_gb) == ram_in_gb:
        return f"{int(ram_in_gb)}G"
    else:
        return f"{round(int(ram_in_gb * 1024))}M"


def get_partition_str(partition):
    if partition is None:
        if "SLURMZY_DEFAULT_PARTITION" in os.environ:
            partition = os.environ["SLURMZY_DEFAULT_PARTITION"]
        else:
            return None

    return f"#SBATCH --partition={partition}"


def get_array_str(start, end, limit=10):
    if (start is None and end is not None) or (end is None and start is not None):
        raise Exception(
            f"start, end must be both used, or neither used. start={start}, end={end}"
        )

    if start is not None:
        return f"#SBATCH --array={start}-{end}%{limit}"
    else:
        return None


def after_ok_str(after_ok):
    if after_ok is None:
        return None

    return f"#SBATCH --dependency=afterok:{after_ok}"


def submit_job(
    command,
    name,
    ram_gb,
    time_hours,
    out_err_prefix=None,
    dry_run=False,
    cpus=1,
    partition=None,
    array_start=None,
    array_end=None,
    array_limit=10,
    after_ok=None,
):
    ram = convert_ram(ram_gb)
    array_str = get_array_str(array_start, array_end, array_limit)
    extra_opts = [
        get_partition_str(partition),
        array_str,
        after_ok_str(after_ok),
    ]
    extra_opts = "\n".join([x for x in extra_opts if x is not None])

    if out_err_prefix is None:
        out_err_prefix = name

    if array_str is None:
        time_outfile = f"{out_err_prefix}.o"
    else:
        out_err_prefix += ".%a"
        command = command.replace("SLURM_ARRAY_TASK_ID", "$SLURM_ARRAY_TASK_ID")
        time_outfile = f"{out_err_prefix}.$SLURM_ARRAY_TASK_ID.o"

    # Time is a float in hours. sbatch can take it in a few forms, but easiest
    # here is default of an integer specifying the number of minutes.
    time_mins = int(round(time_hours * 60))

    # Create the job script
    job_script = (
        f"""#!/usr/bin/env bash
#SBATCH --job-name={name}
#SBATCH --output={out_err_prefix}.o
#SBATCH --error={out_err_prefix}.e
#SBATCH --mem={ram}
#SBATCH --time={time_mins}
#SBATCH --cpus-per-task={cpus}
#SBATCH --signal=B:SIGUSR1@60
{extra_opts}

start_time=$(date +"%Y-%m-%dT%H:%M:%S")
start_seconds=$(date +%s)

end_time=RUNNING
exit_code=UNKNOWN

gather_stats() """
        + "{"
        + f"""
# unset the trap otherwise this function can get called more than once
trap - EXIT SIGUSR1
end_time=$(date +"%Y-%m-%dT%H:%M:%S")
end_seconds=$(date +%s)
wall_clock_s=$(($end_seconds-$start_seconds))
echo -e "SLURM_STATS_BEGIN
SLURM_STATS\tjob_id\t$SLURM_JOB_ID
SLURM_STATS\tcommand\t{command}
SLURM_STATS\trequested_ram\t{ram_gb}
SLURM_STATS\trequested_time\t{time_mins}
SLURM_STATS\tjob_name\t{name}
SLURM_STATS\tstart_time\t$start_time
SLURM_STATS\tend_time\t$end_time
SLURM_STATS\twall_clock_s\t$wall_clock_s
SLURM_STATS\texit_code\t$exit_code"
slurmzy jobinfo $SLURM_JOB_ID | """
        + """ awk '{print "SLURM_STATS_JOBINFO\t"$0}'

if [ $exit_code = "UNKNOWN" ]
then
    exit 1
else
    exit $exit_code
fi
}
"""
        + f"""
trap gather_stats EXIT SIGUSR1

/usr/bin/time -a -o {time_outfile} -v $SHELL -c "$(cat << 'EOF'
{command}
EOF
)"

exit_code=$?
gather_stats
"""
    )

    if dry_run:
        print(job_script)
        return job_script
    else:
        process = subprocess.run(["sbatch"], input=job_script, text=True, check=True)


def run(options):
    # command line options is a list of all strings at end of command.
    # Want a single string
    options.command = " ".join(options.command)
    submit_job(
        options.command,
        options.name,
        options.ram,
        options.time,
        out_err_prefix=options.oe,
        dry_run=options.norun,
        cpus=options.cpus,
        partition=options.queue,
        array_start=options.array_start,
        array_end=options.array_end,
        array_limit=options.array_limit,
        after_ok=options.afterok,
    )
