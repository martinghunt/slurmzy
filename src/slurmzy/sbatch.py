import subprocess


def convert_ram(ram_in_gb):
    if int(ram_in_gb) == ram_in_gb:
        return f"{int(ram_in_gb)}G"
    else:
        return f"{round(int(ram_in_gb * 1024))}M"


def submit_job(command, name, ram_gb, time_hours, dry_run=False, cpus=1):
    ram = convert_ram(ram_gb)

    # Time is a float in hours. sbatch can take it in a few forms, but easiest
    # here is default of an integer specifying the number of minutes
    time_mins = int(round(time_hours * 60))

    # Create the job script
    job_script = f"""#!/usr/bin/env bash
#SBATCH --job-name={name}
#SBATCH --output={name}.o
#SBATCH --error={name}.e
#SBATCH --mem={ram}
#SBATCH --time={time_mins}
#SBATCH --cpus_per_task={cpus}

set -o pipefail
start_time=$(date +"%Y-%m-%dT%H:%M:%S")
/usr/bin/time -o /dev/stdout -v $SHELL -c "$(cat << 'EOF'
{command}
EOF
)"
exit_code=$?
end_time=$(date +"%Y-%m-%dT%H:%M:%S")

echo -e "
SLURM_STATS_BEGIN
SLURM_STATS\tcommand\t{command}
SLURM_STATS\tstart_time\t$start_time
SLURM_STATS\tend_time\t$end_time
SLURM_STATS\texit_code\t$exit_code"
seff $SLURM_JOB_ID | awk '""" + '{print "SLURM_STATS_SEFF\t"$0}' + """'
exit $exit_code
"""

    if dry_run:
        print(job_script)
        return(job_script)
    else:
        process = subprocess.run(['sbatch'], input=job_script, text=True, check=True)



def run(options):
    # command line options is a list of all strings at end of command.
    # Want a single string
    options.command = " ".join(options.command)
    submit_job(
        options.command,
        options.name,
        options.ram,
        options.time,
        dry_run=options.dry_run,
        cpus=options.cpus,
    )
