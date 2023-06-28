# slurmzy

Slurm wrapper scripts


## Install

It's pure python, with no dependencies. Run:

```
python3 -m pip install .
```

to install the script `slurmzy`


## Submit job

Run a job with:

```
slurmzy run <memory in GB> <name> <command>
```

By default it sets a time limit of 1 hour. Change this to limit to
`N` hours  with `--time N`.

The job will write all `stdout` to the file `name.o`, and all `stderr` to
`name.e`. It will also add some job stats at the end of `name.o`: the output
of `/usr/bin/time -v`, and some more stats. This is a basic attempt to
reproduce what LSF does (but more grep-friendly). It also gets the
output of `seff` on the job at the end, but since the job has not
yet finished, the output is of limited use (and the state is "RUNNING").

The end of the `name.o` file looks like this:

```
	Command being timed: "/usr/local/bin/bash -c echo test"
	User time (seconds): 0.00
	System time (seconds): 0.00
...skip lots of lines from time -v to save space in this README...
	Page size (bytes): 4096
	Exit status: 0

SLURM_STATS_BEGIN
SLURM_STATS	command	echo test
SLURM_STATS	start_time	2023-06-28T13:47:33
SLURM_STATS	end_time	2023-06-28T13:47:33
SLURM_STATS	exit_code	0
SLURM_STATS_SEFF	Job ID: 4242424242
SLURM_STATS_SEFF	Cluster: cluster_name
SLURM_STATS_SEFF	User/Group: lee/rush
SLURM_STATS_SEFF	State: RUNNING
SLURM_STATS_SEFF	Cores: 1
SLURM_STATS_SEFF	CPU Utilized: 00:00:00
SLURM_STATS_SEFF	CPU Efficiency: 0.00% of 00:00:00 core-walltime
SLURM_STATS_SEFF	Job Wall-clock time: 00:00:00
SLURM_STATS_SEFF	Memory Utilized: 0.00 MB (estimated maximum)
SLURM_STATS_SEFF	Memory Efficiency: 0.00% of 102.00 MB (102.00 MB/node)
SLURM_STATS_SEFF	WARNING: Efficiency statistics may be misleading for RUNNING jobs.
```


## Get stats of finished jobs

To do
