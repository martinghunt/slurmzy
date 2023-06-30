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
            return ""

    return f"#SBATCH --partition={partition}"


def submit_job(
    command, name, ram_gb, time_hours, dry_run=False, cpus=1, partition=None
):
    ram = convert_ram(ram_gb)
    partition = get_partition_str(partition)

    # Time is a float in hours. sbatch can take it in a few forms, but easiest
    # here is default of an integer specifying the number of minutes.
    time_mins = int(round(time_hours * 60))

    # Create the job script
    job_script = f"""#!/usr/bin/env bash
#SBATCH --job-name={name}
#SBATCH --output={name}.o
#SBATCH --error={name}.e
#SBATCH --mem={ram}
#SBATCH --time={time_mins}
#SBATCH --cpus-per-task={cpus}
#SBATCH --signal=B:SIGUSR1@60
{partition}

start_time=$(date +"%Y-%m-%dT%H:%M:%S")
start_seconds=$(date +%s)


end_time=RUNNING
exit_code=UNKNOWN

gather_stats() """ + "{" + f"""
# unset the trap otherwise this function can get called more than once
trap - EXIT SIGUSR1
end_time=$(date +"%Y-%m-%dT%H:%M:%S")
end_seconds=$(date +%s)
wall_clock_s=$(($end_seconds-$start_seconds))
echo -e "SLURM_STATS_BEGIN
SLURM_STATS\tcommand\t{command}
SLURM_STATS\trequested_ram\t{ram_gb}
SLURM_STATS\tjob_name\t{name}
SLURM_STATS\tstart_time\t$start_time
SLURM_STATS\tend_time\t$end_time
SLURM_STATS\twall_clock_s\t$wall_clock_s
SLURM_STATS\texit_code\t$exit_code"
seff $SLURM_JOB_ID | """ + """ awk '{print "SLURM_STATS_SEFF\t"$0}'

if [ $exit_code = "UNKNOWN" ]
then
    exit 1
else
    exit $exit_code
fi
}
""" + f"""
trap gather_stats EXIT SIGUSR1

set -o pipefail
/usr/bin/time -a -o {name}.o -v $SHELL -c "$(cat << 'EOF'
{command}
EOF
)"

exit_code=$?
gather_stats
"""

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
        dry_run=options.norun,
        cpus=options.cpus,
        partition=options.queue,
    )
