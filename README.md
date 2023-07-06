# slurmzy

Slurm wrapper scripts.


## Install

It's pure python, with no dependencies (apart from assuming Slurm
is installed, obviously). Run:

```
python3 -m pip install .
```

to install the script `slurmzy`


## Acknowledgements

This repo contains a copy of the excellent `jobinfo` script from
https://github.com/birc-aeh/slurm-utils/tree/master

## tl;dr synopsis

Submit a job asking for 1GB RAM, called `my_job`, that runs the script
`my_script`:

```
slurmzy run 1 my_job my_script
```

It will write `stdout`, and job stats (eg run time, memory etc) to the file
`my_job.o`, and `stderr` to the file `my_job.e`.

Get a summary of the job, when it has finished:

```
slurmzy ostats my_job.o
```


## Submit job

Run a job with:

```
slurmzy run <memory in GB> <name> <command>
```

Notes:

* By default it sets a time limit of 1 hour. Change this to limit to
  `N` hours  with `--time N`.
* The default queue/partition is slurm's default, unless you have
  the environment variable `SLURMZY_DEFAULT_PARTITION` set, in which case
  that is used. Either way, the option `--queue` overrides the default.


The job will write all `stdout` to the file `name.o`, and all `stderr` to
`name.e`. It will also add some job stats at the end of `name.o`: the output
of `/usr/bin/time -v`, and some more stats. This is a basic attempt to
reproduce what LSF does (but more grep-friendly). It also gets the
output of `jobinfo` on the job at the end, but since the job has not
yet finished, the output is of limited use (and the state is probably "RUNNING").


The options to `run` are:

```
  --norun               Do not submit job. Print the script that would be submitted
  --array_start INT     Start index of job array
  --array_end INT       End index of job array
  --array_limit INT     Max array elements allowed to run [10]
  -c INT, --cpus INT    Number of cpus [1]
  -q QUEUE_NAME, --queue QUEUE_NAME
                        Queue ('partition') to use instead of default
  -t FLOAT, --time FLOAT
                        Time limit in hours [1]
```

### Job arrays

To run a job array, use the `--array_start` and `--array_end` options
to specify the first and last indexes. They must both be used.
The option `--array_limit` limits the total job elements allowed to
run at any time.

To help stop driving yourself mad with escaping special characters,
if you put `SLURM_ARRAY_TASK_ID` in the
command, it will be replaced with `$SLURM_ARRAY_TASK_ID` (ie `$` added)
in the command that is run.

Toy example:

```
slurmzy run --array_start 1 --array_end 3 0.1 name echo array index is SLURM_ARRAY_TASK_ID
```

This submits a job array with 3 elements. Each job simply runs this command:

```
echo array index is $SLURM_ARRAY_TASK_ID
```

Job 1 prints `array index is 1`, and similarly for jobs 2 and 3.

The output files are called `name.1.o`, `name.2.o`, `name.3.o`, and similarly
for the `.e` error files.


## Get stats of finished jobs

Run this to get a summary of jobs from a list of output `.o` files:

```
slurmzy ostats *.o
```

That will summarise all `.o` files in your current directory. It outputs
to stdtout in TSV format. Example:

```
slurmzy ostats -f *.o | column -t
exit_code  system_time_h  wall_clock_h  max_ram  requested_ram  nodes  filename
0          0.2            0.21          1.01     1.6            node1  happy.o
137        1.0            1.1           2.01     1.0            node2  too_much_ram.o
TIMEOUT    None           0.02          None     0.1            node3  hit_time_limit.o
```

In that example, the first job ran OK (`exit_code` zero), the second
hit the memory limit, and the third job hit the time limit.
Except for `TIMEOUT`, the `exit_code` will be the actual exit code from
the command you ran.

The RAM is in GB.

When everything runs ok, all the columns should have sensible entries.
When things fail, some columns do not have information (this is a work
in progess and things may improve).

Any `.o` files that have no run information will be ignored, and not
appear in the output. This means you can safely get the stats of
jobs where you know some will still be running. For example
running `slurmzy ostats *.o` gets stats of all the finished
jobs in your current directory and not report on the jobs that are
in progress.

Options to `ostats` are:

```
  -a, --all_columns   Output all columns
  -f, --fails         Output only failed jobs
  --time_units s|m|h  Time units to report, h (hours), m (minutes), s (seconds) [h]
```

### Known issues

RAM and cpu time are not reported by `ostats` if the job fails because of a
timeout or because it was cancelled with `scancel`.

The output of `jobinfo` is put into the `.o` file. This is the last thing
that is run, but the job is still running under slurm.
This means the contents are not reliable, particularly the RAM and CPU stats.
For this reason, we get the CPU and memory from the output
of `/usr/bin/time -v`. However, this output is not always present
if the job is terminated prematurely.
